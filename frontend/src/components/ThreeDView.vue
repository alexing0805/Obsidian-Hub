<template>
  <div ref="container" class="w-full h-full" @click="onCanvasClick">
    <canvas ref="canvas" class="w-full h-full"></canvas>

    <!-- 拖拽中的实体信息 -->
    <div v-if="draggingEntity || selectedEntity"
      class="absolute top-3 left-3 glass-effect rounded-xl px-4 py-3 text-xs w-56">
      <div class="text-white/70 mb-2 font-medium">拖拽中: {{ draggingEntity.label || draggingEntity.entity_id }}</div>
      <div class="flex items-center gap-2 mb-1">
        <span class="text-white/40 shrink-0">高度 Z:</span>
        <input type="range" min="0" max="800" step="10"
          :value="Math.round(((draggingEntity || selectedEntity)?.z || 0.5) * 1000)"
          class="flex-1 h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer accent-cyan-400"
          @input="onHeightChange" />
        <span class="text-cyan-300 w-10 text-right">{{ Math.round((draggingEntity.z || 0.5) * 1000) }}</span>
      </div>
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
      <div class="glass-effect rounded-2xl p-4 w-96 max-h-[70vh] overflow-y-auto">
        <div class="text-sm font-bold mb-3">添加到视图</div>
        <div v-for="group in groupedAvailableEntities" :key="group.type" class="mb-3">
          <div class="text-xs font-bold text-white/40 mb-1 uppercase">{{ group.icon }} {{ group.type }}</div>
          <div class="space-y-0.5">
            <div v-for="entity in group.entities" :key="entity.entity_id"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-white/10 cursor-pointer text-xs"
              @click="addEntity(entity)">
              <span>{{ entityIcon(entity) }}</span>
              <span class="flex-1 truncate text-white/70">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
            </div>
            <div v-if="!group.entities.length" class="text-xs text-white/20 px-3 py-1">无</div>
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
const isDragging = ref(false)
const selectedEntity = ref(null)

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

const groupedAvailableEntities = computed(() => {
  const groups = {}
  availableEntities.value.forEach(e => {
    const type = entityType(e)
    if (!groups[type]) groups[type] = []
    groups[type].push(e)
  })
  const order = ['灯', '空调', '开关', '传感器', '其他']
  return order
    .filter(t => groups[t])
    .map(type => ({
      type,
      icon: { '灯': '💡', '空调': '❄️', '开关': '🔌', '传感器': '🌡️', '其他': '📦' }[type],
      entities: groups[type],
    }))
    .concat(
      Object.keys(groups)
        .filter(t => !order.includes(t))
        .map(type => ({ type, icon: '📦', entities: groups[type] }))
    )
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
  camera.updateProjectionMatrix()

  // Restore camera from localStorage
  try {
    const saved = localStorage.getItem('3dview_camera')
    if (saved) {
      const { pos, tgt } = JSON.parse(saved)
      camera.position.set(pos.x, pos.y, pos.z)
      controls.target.set(tgt.x, tgt.y, tgt.z)
      controls.update()
    }
  } catch(e) {}

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
  controls.enabled = editMode.value  // Only enabled in edit mode

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
  // Furniture
  buildFurniture()

  // Raycaster
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()

  // Initial entity meshes
  rebuildEntityMeshes()

  // Animation loop
  animate()
}

const buildRoom = () => {
  // Floor with tile-like pattern
  const floorGeo = new THREE.PlaneGeometry(ROOM_W, ROOM_D)
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x1e1e32,
    roughness: 0.85,
    metalness: 0.05,
  })
  roomMesh = new THREE.Mesh(floorGeo, floorMat)
  roomMesh.rotation.x = -Math.PI / 2
  roomMesh.receiveShadow = true
  scene.add(roomMesh)

  // Grid lines
  const grid = new THREE.GridHelper(Math.max(ROOM_W, ROOM_D), 24, 0x2a2a44, 0x1e1e30)
  grid.position.y = 1
  scene.add(grid)

  // Walls
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x2e2e48, roughness: 0.8, metalness: 0.1 })
  const wallH = WALL_H
  const walls = [
    { w: ROOM_W, d: 30, x: 0, z: -ROOM_D / 2 },
    { w: ROOM_W, d: 30, x: 0, z: ROOM_D / 2 },
    { w: 30, d: ROOM_D, x: -ROOM_W / 2, z: 0 },
    { w: 30, d: ROOM_D, x: ROOM_W / 2, z: 0 },
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

const buildFurniture = () => {
  const mat = (color, roughness = 0.7, metalness = 0.1) =>
    new THREE.MeshStandardMaterial({ color, roughness, metalness })


  // Sofa (L-shape)
  const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(900, 120, 400), mat(0x3a3a5c, 0.9))
  sofaBase.position.set(-1800, 60, 2000)
  sofaBase.castShadow = true; sofaBase.receiveShadow = true
  scene.add(sofaBase)
  const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(900, 200, 60), mat(0x3a3a5c, 0.9))
  sofaBack.position.set(-1800, 180, 2200); sofaBack.castShadow = true
  scene.add(sofaBack)
  const sofaArmL = new THREE.Mesh(new THREE.BoxGeometry(60, 180, 400), mat(0x3a3a5c, 0.9))
  sofaArmL.position.set(-2250, 150, 2000); sofaArmL.castShadow = true
  scene.add(sofaArmL)

  // TV console
  const tvCons = new THREE.Mesh(new THREE.BoxGeometry(1400, 80, 200), mat(0x2a2a40, 0.8))
  tvCons.position.set(-1800, 40, -2100); tvCons.castShadow = true; tvCons.receiveShadow = true
  scene.add(tvCons)
  // TV screen
  const tv = new THREE.Mesh(new THREE.BoxGeometry(1200, 700, 20), mat(0x111122, 0.2, 0.8))
  tv.position.set(-1800, 430, -2100); tv.castShadow = true
  scene.add(tv)
  const tvFrame = new THREE.Mesh(new THREE.BoxGeometry(1240, 740, 15), mat(0x222233, 0.3, 0.9))
  tvFrame.position.set(-1800, 430, -2108); tvFrame.castShadow = true
  scene.add(tvFrame)

  // Coffee table
  const coffeeTable = new THREE.Mesh(new THREE.BoxGeometry(600, 30, 300), mat(0x4a3a2a, 0.8))
  coffeeTable.position.set(-1800, 60, 900); coffeeTable.castShadow = true; coffeeTable.receiveShadow = true
  scene.add(coffeeTable)
  const ctLeg = (x, z) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(12, 12, 60, 6), mat(0x333333, 0.6, 0.8))
    leg.position.set(x, 30, z); leg.castShadow = true
    scene.add(leg)
  }
  ctLeg(-2100, 750); ctLeg(-1500, 750); ctLeg(-2100, 1050); ctLeg(-1500, 1050)

  // Dining table
  const dTable = new THREE.Mesh(new THREE.BoxGeometry(900, 50, 500), mat(0x3a2a1a, 0.85))
  dTable.position.set(2800, 80, 1500); dTable.castShadow = true; dTable.receiveShadow = true
  scene.add(dTable)
  const dtLeg = (x, z) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(15, 15, 80, 8), mat(0x333333, 0.6, 0.8))
    leg.position.set(x, 40, z); leg.castShadow = true
    scene.add(leg)
  }
  dtLeg(2450, 1250); dtLeg(3150, 1250); dtLeg(2450, 1750); dtLeg(3150, 1750)

  // Chairs (4)
  const chairSeat = new THREE.BoxGeometry(180, 20, 180)
  const chairBack = new THREE.BoxGeometry(180, 160, 20)
  const chairLeg = new THREE.CylinderGeometry(10, 10, 80, 6)
  const chairPositions = [
    [2800 - 300, 1500], [2800 + 300, 1500],
    [2800, 1500 - 300], [2800, 1500 + 300],
  ]
  const chairRotations = [0, 0, Math.PI / 2, Math.PI / 2]
  chairPositions.forEach(([x, z], i) => {
    const seat = new THREE.Mesh(chairSeat, mat(0x4a3a2a, 0.9))
    seat.position.set(x, 80, z); seat.castShadow = true; seat.receiveShadow = true
    seat.rotation.y = chairRotations[i]
    scene.add(seat)
    const back = new THREE.Mesh(chairBack, mat(0x4a3a2a, 0.9))
    back.position.set(x + Math.sin(chairRotations[i]) * 90, 200, z + Math.cos(chairRotations[i]) * 90)
    back.rotation.y = chairRotations[i]
    back.castShadow = true
    scene.add(back)
    const legPos = [
      [x - 60, z - 60], [x + 60, z - 60],
      [x - 60, z + 60], [x + 60, z + 60],
    ]
    legPos.forEach(([lx, lz]) => {
      const l = new THREE.Mesh(chairLeg, mat(0x333333, 0.6, 0.8))
      l.position.set(lx, 40, lz); l.castShadow = true
      scene.add(l)
    })
  })

  // Bookshelf / storage unit
  const shelf = new THREE.Mesh(new THREE.BoxGeometry(200, 600, 400), mat(0x3a2a1a, 0.85))
  shelf.position.set(ROOM_W / 2 - 130, 300, -1200); shelf.castShadow = true; shelf.receiveShadow = true
  scene.add(shelf)
  // Shelf dividers
  for (let row = 0; row < 3; row++) {
    const divider = new THREE.Mesh(new THREE.BoxGeometry(190, 8, 390), mat(0x4a3a2a, 0.85))
    divider.position.set(ROOM_W / 2 - 130, 120 + row * 160, -1200)
    divider.castShadow = true
    scene.add(divider)
  }

  // Area rug under sofa
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(2000, 1600), mat(0x2a2a44, 0.95))
  rug.rotation.x = -Math.PI / 2
  rug.position.set(-1800, 2, 1800)
  rug.receiveShadow = true
  scene.add(rug)
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

  const entityZ = (mapping.z !== undefined ? mapping.z : 0.5) * 1000  // z is 0-1 normalized -> mm
  const mesh = new THREE.Mesh(geometry, material)
  mesh.position.set(wx, entityZ + (geometry.parameters?.height ? geometry.parameters.height / 2 : 30), wz)
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
    pl.position.set(wx, entityZ + 500, wz)
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
      pl.position.set(wx, entityZ + 500, wz)
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

    if (editMode.value) {
      // Select entity (show height info) but don't start dragging yet
      selectedEntity.value = mapping
      draggingEntity.value = mapping
      isDragging.value = false
    } else {
      // Toggle
      emit('entity-toggle', { entity_id, type })
    }
  } else if (!editMode.value) {
    selectedEntity.value = null
    draggingEntity.value = null
  }
}

const onMouseMove = (event) => {
  // Start dragging on first mouse move with left button held
  if (!isDragging.value && event.buttons === 1 && draggingEntity.value && editMode.value) {
    isDragging.value = true
    if (controls) controls.enabled = false
  }
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

const onHeightChange = (event) => {
  const target = draggingEntity.value || selectedEntity.value
  if (!target) return
  const z = parseInt(event.target.value) / 1000
  draggingEntity.value = { ...target, z }
  const entry = entityMeshes[target.entity_id]
  if (entry) {
    entry.mesh.position.y = z
  }
}

const onMouseUp = () => {
  if (isDragging.value) {
    isDragging.value = false
    if (controls) controls.enabled = editMode.value
  }
  selectedEntity.value = null
  draggingEntity.value = null
}

const savePositions = () => {
  const updated = props.entityMapping.map(m => {
    const entry = entityMeshes[m.entity_id]
    if (entry) {
      const pt = entry.mesh.position
      const { x, y } = toNormalized(pt.x, pt.z)
      const z = pt.y / 1000  // Y position is Z height in mm
      return { ...m, x, y, z }
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

// Watch editMode: enable/disable controls
watch(editMode, (val) => {
  if (controls) controls.enabled = val
})

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
