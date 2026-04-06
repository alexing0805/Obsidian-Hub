<template>
  <div ref="container" class="w-full h-full" @click="onCanvasClick">
    <canvas ref="canvas" class="w-full h-full"></canvas>

    <!-- 拖拽中的实体信息 -->
    <div v-if="draggingEntity"
      class="absolute top-3 left-3 glass-effect rounded-lg px-3 py-1.5 text-xs text-white/70">
      拖拽中: {{ draggingEntity.label || draggingEntity.entity_id }}
    </div>

    <!-- 编辑模式开关 -->
    <div class="absolute top-3 right-3 flex gap-2">
      <button v-if="editMode"
        class="glass-effect rounded-lg px-3 py-1.5 text-xs text-emerald-400 border border-emerald-500/40"
        @click="savePositions">💾 保存位置</button>
      <button
        class="glass-effect rounded-lg px-3 py-1.5 text-xs"
        :class="editMode ? 'text-cyan-400 border border-cyan-500/40' : 'text-white/50 border border-white/10'"
        @click="editMode = !editMode">
        {{ editMode ? '✅ 编辑模式' : '✏️ 编辑位置' }}
      </button>
    </div>

    <!-- 添加实体按钮（编辑模式下） -->
    <div v-if="editMode && showEntityPicker" class="absolute inset-0 z-20 flex items-center justify-center bg-black/60" @click.self="showEntityPicker = false">
      <div class="glass-effect rounded-2xl p-4 w-80 max-h-[70vh] overflow-y-auto">
        <div class="text-sm font-bold mb-3">添加到视图</div>
        <div class="space-y-1">
          <div v-for="entity in availableEntities" :key="entity.entity_id"
            class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/10 cursor-pointer text-sm"
            @click="addEntity(entity)">
            <span>{{ entityIcon(entity) }}</span>
            <span class="flex-1 truncate text-white/70">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
            <span class="text-xs text-white/30">{{ entityType(entity) }}</span>
          </div>
        </div>
      </div>
    </div>

    <button v-if="editMode"
      class="absolute bottom-3 right-3 glass-effect rounded-xl px-4 py-2 text-sm text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/10"
      @click="showEntityPicker = true">
      ➕ 添加实体到视图
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  entityMapping: { type: Array, default: () => [] },
})

const emit = defineEmits(['entity-toggle', 'mapping-update', 'entity-add', 'entity-remove'])

const container = ref(null)
const canvas = ref(null)
const editMode = ref(false)
const showEntityPicker = ref(false)
const draggingEntity = ref(null)

// Three.js refs
let scene, camera, renderer, controls
let entityMeshes = {}  // entity_id -> { mesh, light, glowMesh, type }
let roomMesh = null
let raycaster, mouse
let hoveredMesh = null

// Room dimensions (normalized 0-1 mapped to these mm units)
const ROOM_W = 12000
const ROOM_D = 10000
const WALL_H = 300

// Lights
let ambientLight
let pointLights = {}  // entity_id -> THREE.PointLight

const entityType = (entity) => {
  if (entity.entity_id.startsWith('light.')) return '灯'
  if (entity.entity_id.startsWith('climate.')) return '空调'
  if (entity.entity_id.startsWith('sensor.')) return '传感器'
  if (entity.entity_id.startsWith('switch.')) return '开关'
  return '其他'
}

const entityIcon = (entity) => {
  if (entity.entity_id.startsWith('light.')) return '💡'
  if (entity.entity_id.startsWith('climate.')) return '❄️'
  if (entity.entity_id.startsWith('sensor.')) return '🌡️'
  if (entity.entity_id.startsWith('switch.')) return '🔌'
  return '📦'
}

const entityColor = (entity) => {
  if (entity.entity_id.startsWith('light.')) return entity.state === 'on' ? 0xffdd44 : 0x666666
  if (entity.entity_id.startsWith('climate.')) return 0x4499ff
  if (entity.entity_id.startsWith('sensor.')) return 0x44ffaa
  if (entity.entity_id.startsWith('switch.')) return entity.state === 'on' ? 0x44ff44 : 0x666666
  return 0x888888
}

const availableEntities = computed(() => {
  const mappedIds = new Set(props.entityMapping.map(e => e.entity_id))
  return props.haEntities.filter(e => !mappedIds.has(e.entity_id))
})

// Convert entity mapping position (0-1) to world coords
const toWorld = (x, y) => ({
  x: (x - 0.5) * ROOM_W,
  z: (y - 0.5) * ROOM_D,
})

const toNormalized = (wx, wz) => ({
  x: wx / ROOM_W + 0.5,
  y: wz / ROOM_D + 0.5,
})

const initThree = () => {
  const w = canvas.value.clientWidth
  const h = canvas.value.clientHeight

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a0a14)
  scene.fog = new THREE.Fog(0x0a0a14, ROOM_W * 1.5, ROOM_W * 3)

  // Camera (top-down with slight angle)
  camera = new THREE.PerspectiveCamera(45, w / h, 1, 50000)
  camera.position.set(0, ROOM_W * 1.2, 0)
  camera.lookAt(0, 0, 0)

  // Renderer
  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.maxPolarAngle = Math.PI / 2.2
  controls.minDistance = 500
  controls.maxDistance = ROOM_W * 3

  // Ambient
  ambientLight = new THREE.AmbientLight(0x222233, 0.4)
  scene.add(ambientLight)

  // Directional light (sun)
  const sun = new THREE.DirectionalLight(0xffeedd, 0.3)
  sun.position.set(ROOM_W, ROOM_W * 2, ROOM_D * 0.5)
  sun.castShadow = true
  sun.shadow.mapSize.set(2048, 2048)
  sun.shadow.camera.near = 100
  sun.shadow.camera.far = ROOM_W * 5
  sun.shadow.camera.left = -ROOM_W
  sun.shadow.camera.right = ROOM_W
  sun.shadow.camera.top = ROOM_D
  sun.shadow.camera.bottom = -ROOM_D
  scene.add(sun)

  // Room floor
  buildRoom()

  // Raycaster
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()

  // Initial entity meshes
  rebuildEntityMeshes()

  // Animation loop
  animate()
}

const buildRoom = () => {
  // Floor
  const floorGeo = new THREE.PlaneGeometry(ROOM_W, ROOM_D)
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a2e,
    roughness: 0.9,
    metalness: 0.1,
  })
  roomMesh = new THREE.Mesh(floorGeo, floorMat)
  roomMesh.rotation.x = -Math.PI / 2
  roomMesh.receiveShadow = true
  scene.add(roomMesh)

  // Grid
  const grid = new THREE.GridHelper(Math.max(ROOM_W, ROOM_D), 20, 0x333355, 0x222244)
  grid.position.y = 1
  scene.add(grid)

  // Walls (thin boxes)
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x2a2a40, roughness: 0.8 })
  const wallH = WALL_H
  const walls = [
    { w: ROOM_W, d: 30, x: 0, z: -ROOM_D / 2 },  // north
    { w: ROOM_W, d: 30, x: 0, z: ROOM_D / 2 },   // south
    { w: 30, d: ROOM_D, x: -ROOM_W / 2, z: 0 }, // west
    { w: 30, d: ROOM_D, x: ROOM_W / 2, z: 0 },  // east
  ]
  walls.forEach(({ w, d, x, z }) => {
    const geo = new THREE.BoxGeometry(w, wallH, d)
    const mesh = new THREE.Mesh(geo, wallMat)
    mesh.position.set(x, wallH / 2, z)
    mesh.castShadow = true
    mesh.receiveShadow = true
    scene.add(mesh)
  })
}

const rebuildEntityMeshes = () => {
  // Clear old
  Object.values(entityMeshes).forEach(({ mesh, glowMesh }) => {
    scene.remove(mesh)
    if (glowMesh) scene.remove(glowMesh)
  })
  Object.values(pointLights).forEach(l => scene.remove(l))
  pointLights = {}
  entityMeshes = {}

  props.entityMapping.forEach(mapping => {
    const entity = props.haEntities.find(e => e.entity_id === mapping.entity_id)
    if (!entity) return
    createEntityMesh(entity, mapping)
  })
}

const createEntityMesh = (entity, mapping) => {
  const { x: wx, z: wz } = toWorld(mapping.x || 0.5, mapping.y || 0.5)
  const type = mapping.type || entityType(entity)
  const isLight = entity.entity_id.startsWith('light.')
  const isOn = entity.state === 'on'

  // Base marker size
  const size = type === '灯' ? 120 : (type === '空调' ? 160 : 100)

  let geometry, material
  if (type === '灯') {
    geometry = new THREE.CylinderGeometry(size * 0.4, size * 0.5, 60, 8)
    material = new THREE.MeshStandardMaterial({
      color: isOn ? 0xffdd44 : 0x555555,
      emissive: isOn ? 0xffaa00 : 0x000000,
      emissiveIntensity: isOn ? 2 : 0,
      roughness: 0.3,
      metalness: 0.7,
    })
  } else if (type === '空调') {
    geometry = new THREE.BoxGeometry(size * 0.8, 50, size * 0.3)
    material = new THREE.MeshStandardMaterial({
      color: 0x4488cc,
      emissive: isOn ? 0x003366 : 0x000000,
      emissiveIntensity: isOn ? 0.5 : 0,
      roughness: 0.3,
      metalness: 0.5,
    })
  } else if (type === '传感器' || type === '温度计') {
    geometry = new THREE.SphereGeometry(size * 0.35, 16, 16)
    material = new THREE.MeshStandardMaterial({
      color: 0x44ffaa,
      emissive: 0x00ff88,
      emissiveIntensity: 0.8,
      roughness: 0.2,
      metalness: 0.3,
    })
  } else {
    geometry = new THREE.BoxGeometry(size * 0.5, 40, size * 0.5)
    material = new THREE.MeshStandardMaterial({
      color: isOn ? 0x44ff44 : 0x555555,
      emissive: isOn ? 0x00ff00 : 0x000000,
      emissiveIntensity: isOn ? 1 : 0,
    })
  }

  const mesh = new THREE.Mesh(geometry, material)
  mesh.position.set(wx, geometry.parameters?.height ? geometry.parameters.height / 2 : 30, wz)
  mesh.castShadow = true
  mesh.receiveShadow = true
  mesh.userData = { entity_id: entity.entity_id, mapping, type }
  scene.add(mesh)

  // Glow ring for lights
  let glowMesh = null
  if (type === '灯' && isOn) {
    const glowGeo = new THREE.RingGeometry(size * 0.5, size * 1.2, 32)
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xffdd44,
      transparent: true,
      opacity: 0.15,
      side: THREE.DoubleSide,
    })
    glowMesh = new THREE.Mesh(glowGeo, glowMat)
    glowMesh.rotation.x = -Math.PI / 2
    glowMesh.position.set(wx, 2, wz)
    scene.add(glowMesh)
  }

  // Point light for lights
  if (type === '灯' && isOn) {
    const pl = new THREE.PointLight(0xffdd44, 3, 1500, 1.5)
    pl.position.set(wx, 400, wz)
    pl.castShadow = false
    scene.add(pl)
    pointLights[entity.entity_id] = pl
  }

  entityMeshes[entity.entity_id] = { mesh, glowMesh, type }
}

const updateEntityState = (entity_id) => {
  const entity = props.haEntities.find(e => e.entity_id === entity_id)
  if (!entity) return
  const mapping = props.entityMapping.find(m => m.entity_id === entity_id)
  if (!mapping) return

  const entry = entityMeshes[entity_id]
  if (!entry) return

  const isLight = entity.entity_id.startsWith('light.')
  const isOn = entity.state === 'on'

  if (isLight) {
    // Update material
    entry.mesh.material.color.setHex(isOn ? 0xffdd44 : 0x555555)
    entry.mesh.material.emissive.setHex(isOn ? 0xffaa00 : 0x000000)
    entry.mesh.material.emissiveIntensity = isOn ? 2 : 0

    // Update glow
    if (entry.glowMesh) {
      entry.glowMesh.visible = isOn
    } else if (isOn) {
      const size = 120
      const glowGeo = new THREE.RingGeometry(size * 0.5, size * 1.2, 32)
      const glowMat = new THREE.MeshBasicMaterial({
        color: 0xffdd44, transparent: true, opacity: 0.15, side: THREE.DoubleSide,
      })
      entry.glowMesh = new THREE.Mesh(glowGeo, glowMat)
      entry.glowMesh.rotation.x = -Math.PI / 2
      const { x: wx, z: wz } = toWorld(mapping.x, mapping.y)
      entry.glowMesh.position.set(wx, 2, wz)
      scene.add(entry.glowMesh)
    }

    // Update point light
    if (pointLights[entity_id]) {
      pointLights[entity_id].intensity = isOn ? 3 : 0
    } else if (isOn) {
      const { x: wx, z: wz } = toWorld(mapping.x, mapping.y)
      const pl = new THREE.PointLight(0xffdd44, 3, 1500, 1.5)
      pl.position.set(wx, 400, wz)
      scene.add(pl)
      pointLights[entity_id] = pl
    }
  } else if (entity.entity_id.startsWith('climate.')) {
    entry.mesh.material.color.setHex(isOn ? 0x4488cc : 0x334455)
    entry.mesh.material.emissive.setHex(isOn ? 0x003366 : 0x000000)
    entry.mesh.material.emissiveIntensity = isOn ? 0.5 : 0
  } else {
    entry.mesh.material.color.setHex(isOn ? 0x44ff44 : 0x555555)
    entry.mesh.material.emissive.setHex(isOn ? 0x00ff00 : 0x000000)
    entry.mesh.material.emissiveIntensity = isOn ? 1 : 0
  }
}

const onCanvasClick = (event) => {
  if (!renderer || !camera) return

  const rect = canvas.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const meshes = Object.values(entityMeshes).map(e => e.mesh)
  const intersects = raycaster.intersectObjects(meshes)

  if (intersects.length > 0) {
    const mesh = intersects[0].object
    const { entity_id, mapping, type } = mesh.userData

    if (editMode) {
      // Start dragging
      draggingEntity.value = mapping
      controls.enabled = false
    } else {
      // Toggle
      emit('entity-toggle', { entity_id, type })
    }
  }
}

const onMouseMove = (event) => {
  if (!draggingEntity.value || !renderer || !camera) return

  const rect = canvas.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)
  const pt = new THREE.Vector3()
  raycaster.ray.intersectPlane(plane, pt)

  if (pt) {
    const { x, y } = toNormalized(pt.x, pt.z)
    draggingEntity.value = { ...draggingEntity.value, x, y }

    // Update mesh position
    const entry = entityMeshes[draggingEntity.value.entity_id]
    if (entry) {
      entry.mesh.position.x = pt.x
      entry.mesh.position.z = pt.z
      if (entry.gMesh) entry.glowMesh.position.set(pt.x, 2, pt.z)
    }
    if (pointLights[draggingEntity.value.entity_id]) {
      pointLights[draggingEntity.value.entity_id].position.set(pt.x, 400, pt.z)
    }
  }
}

const onMouseUp = () => {
  if (draggingEntity.value) {
    draggingEntity.value = null
    controls.enabled = true
  }
}

const savePositions = () => {
  const updated = props.entityMapping.map(m => {
    const entry = entityMeshes[m.entity_id]
    if (entry) {
      const pt = entry.mesh.position
      const { x, y } = toNormalized(pt.x, pt.z)
      return { ...m, x, y }
    }
    return m
  })
  emit('mapping-update', updated)
}

const addEntity = (entity) => {
  emit('entity-add', entity)
  showEntityPicker.value = false
}

const animate = () => {
  if (!renderer) return
  requestAnimationFrame(animate)

  // Animate glow pulse for active lights
  const t = Date.now() * 0.001
  Object.entries(entityMeshes).forEach(([eid, entry]) => {
    if (entry.glowMesh && entry.glowMesh.visible) {
      entry.glowMesh.material.opacity = 0.1 + Math.sin(t * 2) * 0.05
    }
  })

  controls.update()
  renderer.render(scene, camera)
}

const onResize = () => {
  if (!container.value || !renderer || !camera) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

// Watch entity states
watch(() => props.haEntities, (entities) => {
  entities.forEach(e => updateEntityState(e.entity_id))
}, { deep: true })

watch(() => props.entityMapping, () => {
  rebuildEntityMeshes()
}, { deep: true })

onMounted(() => {
  initThree()
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('resize', onResize)
  if (renderer) renderer.dispose()
  if (controls) controls.dispose()
})
</script>
