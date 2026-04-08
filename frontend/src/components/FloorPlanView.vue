<template>
  <div class="w-full h-full relative overflow-hidden rounded-2xl glass-effect">
    <div
      ref="planContainer"
      class="w-full h-full touch-none"
      :style="bgStyle"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      @touchmove.prevent="onTouchMove"
      @touchend="onTouchEnd"
    >
      <div
        v-for="mapping in displayMappings"
        :key="mapping.entity_id"
        class="entity-item absolute flex flex-col items-center cursor-pointer select-none group"
        :style="mapping.style"
        @click.stop="onIconClick(mapping)"
        @mousedown.stop="startDrag(mapping, $event)"
        @touchstart.stop="startTouchDrag(mapping, $event)"
      >
        <div
          v-if="mapping.showGlow"
          class="absolute inset-0 -m-10 rounded-full bg-yellow-400/20 blur-2xl animate-pulse"
        ></div>

        <div
          class="relative w-16 h-16 flex items-center justify-center rounded-2xl glass-panel transition-all duration-300 group-hover:scale-110 group-hover:bg-white/10"
          :class="mapping.panelClass"
        >
          <component
            :is="getIconComponent(mapping.type, mapping.entity_id)"
            class="w-8 h-8 transition-colors duration-300"
            :class="mapping.iconClass"
          />

          <div
            v-if="mapping.value"
            class="absolute -top-3 -right-3 px-2 py-1 bg-cyan-500 text-[10px] font-black text-white rounded-full shadow-lg border border-white/20 select-none z-10"
          >
            {{ mapping.value }}
          </div>

          <div
            v-if="mapping.showIndicator"
            class="absolute top-2 right-2 w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)] bg-white animate-pulse"
          ></div>
        </div>

        <div
          v-if="showLabels"
          class="mt-2.5 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/5 text-sm font-bold tracking-tight text-white/80 whitespace-nowrap overflow-hidden text-ellipsis max-w-[120px] shadow-sm"
        >
          {{ mapping.label || shortId(mapping.entity_id) }}
        </div>
      </div>

      <div
        v-if="dragging"
        class="entity-item absolute flex flex-col items-center pointer-events-none opacity-50"
        :style="previewStyle"
      >
        <div class="w-16 h-16 flex items-center justify-center rounded-2xl glass-panel border-dashed border-cyan-400/50">
          <component :is="getIconComponent(dragMapping?.type, dragMapping?.entity_id)" class="w-8 h-8 text-cyan-400" />
        </div>
      </div>
    </div>

    <template v-if="!kioskMode">
      <div class="absolute bottom-28 right-6 flex flex-col gap-3 z-40">
        <button
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all shadow-lg"
          :class="editMode ? 'text-cyan-300 border border-cyan-500/50 bg-cyan-500/10' : 'border-white/10'"
          @click="editMode = !editMode"
          :title="editMode ? '完成编辑' : '编辑视图'"
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </button>

        <button
          v-if="editMode"
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/10 transition-all shadow-lg"
          @click="showAddDrawer = true"
          title="添加设备"
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
        </button>

        <label
          v-if="editMode"
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-white/60 border border-white/10 hover:bg-white/10 hover:text-white/80 transition-all shadow-lg cursor-pointer"
          title="上传户型图"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <input type="file" accept="image/*" class="hidden" @change="onImageUpload" />
        </label>

        <button
          v-if="editMode && hasChanges"
          class="w-14 h-14 rounded-2xl flex items-center justify-center text-emerald-400 border border-emerald-500/50 bg-emerald-500/10 shadow-lg animate-pulse"
          @click="savePositions"
          title="保存更改"
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </button>
      </div>

      <div v-if="editMode" class="absolute top-4 left-4 flex gap-2 flex-wrap max-w-[60%]">
        <button
          v-for="layer in layers"
          :key="layer"
          class="glass-panel rounded-xl px-4 py-2.5 text-sm font-bold tracking-wider transition-all"
          :class="activeLayer === layer ? 'text-white border-white/30 bg-white/10 shadow-lg' : 'text-white/40 border-white/5 hover:bg-white/5 hover:text-white/60'"
          @click="activeLayer = layer"
        >
          {{ layer }}
        </button>
      </div>

      <div v-if="editMode" class="absolute bottom-6 left-1/2 -translate-x-1/2 glass-effect rounded-xl px-5 py-2.5 text-sm text-white/50 shadow-lg">
        点击图标切换开关 | 拖拽移动位置 | 上传户型图
      </div>
    </template>

    <Teleport to="body">
      <div v-if="showAddDrawer" class="fixed inset-0 z-[100] flex items-center justify-center p-8">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-xl" @click="showAddDrawer = false"></div>
        <div class="relative glass-panel rounded-[2.5rem] w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden shadow-2xl border-white/10 animate-fade-in">
          <div class="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-xl font-heading font-extrabold text-white">添加设备到视图</h3>
            <button class="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all bg-white/5 border border-white/10" @click="showAddDrawer = false">×</button>
          </div>

          <div class="p-4 border-b border-white/5">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索设备，例如 light.kitchen"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-base focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
            />
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-2">
            <div
              v-for="entity in availableEntities"
              :key="entity.entity_id"
              class="flex items-center justify-between p-5 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-all group"
              @click="addEntityToPlan(entity)"
            >
              <div class="flex flex-col min-w-0 flex-1">
                <span class="text-base font-bold text-white truncate">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                <span class="text-xs uppercase tracking-tighter text-white/30 truncate">{{ entity.entity_id }}</span>
              </div>
              <button class="px-4 py-2 rounded-xl bg-cyan-500/20 text-cyan-400 text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity border border-cyan-500/30">
                添加
              </button>
            </div>
            <div v-if="availableEntities.length === 0" class="text-center py-20 text-white/20 text-lg">
              未找到设备
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, h, ref, watch } from 'vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  entityMapping: { type: Array, default: () => [] },
  bgImage: { type: String, default: '' },
  kioskMode: { type: Boolean, default: false }
})

const emit = defineEmits(['mapping-update', 'bg-update', 'entity-toggle', 'open'])

const layers = ['全部', '客厅', '卧室', '厨房', '卫生间', '阳台']

const planContainer = ref(null)
const editMode = ref(false)
const dragging = ref(false)
const dragMapping = ref(null)
const previewPos = ref({ x: 0, y: 0 })
const localMappings = ref([])
const localBgImage = ref('')
const hasChanges = ref(false)
const showAddDrawer = ref(false)
const searchQuery = ref('')
const activeLayer = ref('全部')

const entitiesById = computed(() => {
  const map = new Map()
  for (const entity of props.haEntities) {
    map.set(entity.entity_id, entity)
  }
  return map
})

const availableEntities = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const mappedIds = new Set(localMappings.value.map((mapping) => mapping.entity_id))
  return props.haEntities.filter((entity) => {
    if (mappedIds.has(entity.entity_id)) return false
    const name = String(entity.attributes?.friendly_name || '').toLowerCase()
    const id = entity.entity_id.toLowerCase()
    return name.includes(query) || id.includes(query)
  }).slice(0, 50)
})

const displayMappings = computed(() => {
  const baseMappings = activeLayer.value === '全部'
    ? localMappings.value
    : localMappings.value.filter((mapping) => mapping.layer === activeLayer.value)

  return baseMappings.map((mapping) => {
    const entity = entitiesById.value.get(mapping.entity_id)
    const state = entity?.state || 'off'
    const value = getEntityValue(entity)
    const isOn = state === 'on'
    const isLight = mapping.type === '灯'
    const animated = !props.kioskMode
    const color = isOn ? (isLight ? '#fbbf24' : '#60a5fa') : '#555'

    return {
      ...mapping,
      entity,
      state,
      value,
      showGlow: animated && isOn && isLight,
      showIndicator: animated && isOn && isLight,
      panelClass: isOn ? 'ring-2 ring-white/20' : 'ring-1 ring-white/5',
      iconClass: isOn
        ? (isLight ? 'text-yellow-300 glow-yellow' : 'text-cyan-300 glow-blue')
        : 'text-white/40',
      style: {
        left: `${(mapping.x || 0.5) * 100}%`,
        top: `${(mapping.y || 0.5) * 100}%`,
        transform: 'translate(-50%, -50%)',
        color,
        filter: animated && isOn && isLight ? 'drop-shadow(0 0 8px #fbbf2488)' : 'none',
        zIndex: isOn ? 5 : 4
      }
    }
  })
})

const showLabels = computed(() => editMode.value || activeLayer.value !== '全部')

const bgStyle = computed(() => {
  if (localBgImage.value) {
    return {
      backgroundImage: `url(${localBgImage.value})`,
      backgroundSize: 'contain',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }
  }

  return {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
  }
})

const previewStyle = computed(() => ({
  left: `${previewPos.value.x}px`,
  top: `${previewPos.value.y}px`,
  transform: 'translate(-50%, -50%)',
  color: '#60a5fa'
}))

const addEntityToPlan = (entity) => {
  const newMapping = {
    entity_id: entity.entity_id,
    x: 0.5,
    y: 0.5,
    type: getEntityType(entity.entity_id),
    label: entity.attributes?.friendly_name || entity.entity_id,
    layer: activeLayer.value === '全部' ? '客厅' : activeLayer.value
  }

  localMappings.value = [...localMappings.value, newMapping]
  hasChanges.value = true
  showAddDrawer.value = false
  searchQuery.value = ''
}

const IconLight = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1.3.5 2.6 1.5 3.5.8.8 1.3 1.5 1.5 2.5' }),
  h('path', { d: 'M9 18h6' }),
  h('path', { d: 'M10 22h4' })
])
const IconClimate = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z' })
])
const IconSwitch = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('rect', { width: '18', height: '18', x: '3', y: '3', rx: '2' }),
  h('path', { d: 'M12 8v8' }),
  h('path', { d: 'M8 12h8' })
])
const IconSensor = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M12 2v2M12 20v2M4.93 4.93 6.34 6.34M17.66 17.66 19.07 19.07M2 12h2M20 12h2M6.34 17.66 4.93 19.07M19.07 4.93 17.66 6.34' })
])
const IconCover = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('rect', { width: '18', height: '18', x: '3', y: '3', rx: '2' }),
  h('path', { d: 'M9 3v18' }),
  h('path', { d: 'M15 3v18' })
])
const IconOther = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z' }),
  h('path', { d: 'm3.3 7 8.7 5 8.7-5M12 22V12' })
])

const getIconComponent = (type, entityId = '') => {
  if (entityId.startsWith('cover.')) return IconCover
  return {
    灯: IconLight,
    空调: IconClimate,
    开关: IconSwitch,
    传感器: IconSensor,
    窗帘: IconCover
  }[type] || IconOther
}

const getEntityType = (entityId) => {
  if (entityId.startsWith('light.')) return '灯'
  if (entityId.startsWith('climate.')) return '空调'
  if (entityId.startsWith('switch.')) return '开关'
  if (entityId.startsWith('sensor.')) return '传感器'
  if (entityId.startsWith('cover.')) return '窗帘'
  return '其他'
}

const getEntityValue = (entity) => {
  if (!entity) return null

  if (entity.entity_id.startsWith('climate.')) {
    return `${entity.attributes?.current_temperature || entity.state}°`
  }

  if (entity.entity_id.startsWith('sensor.')) {
    const unit = entity.attributes?.unit_of_measurement || ''
    return entity.state !== 'unknown' ? `${entity.state}${unit}` : null
  }

  if (entity.entity_id.startsWith('cover.')) {
    if (entity.state === 'open') return '开'
    if (entity.state === 'closed') return '关'
    return entity.state
  }

  if (entity.entity_id.startsWith('light.') && entity.state === 'on') {
    const brightness = entity.attributes?.brightness
    if (brightness) return `${Math.round((brightness / 255) * 100)}%`
  }

  return null
}

const shortId = (id) => {
  const parts = id.split('.')
  return parts.length >= 2 ? parts[1].toUpperCase() : id
}

const onIconClick = (mapping) => {
  if (editMode.value) return

  const entity = mapping.entity || entitiesById.value.get(mapping.entity_id)
  const entityId = mapping.entity_id

  if (entityId.startsWith('cover.')) {
    emit('open', { type: 'cover', entityId })
    return
  }

  if (entityId.startsWith('climate.')) {
    emit('open', { type: 'climate', entityId })
    return
  }

  if (entityId.startsWith('sensor.')) {
    emit('open', { type: 'sensor', entityId })
    return
  }

  emit('entity-toggle', entity || mapping)
}

const getClientPos = (event) => {
  if (event.touches && event.touches.length > 0) {
    return { x: event.touches[0].clientX, y: event.touches[0].clientY }
  }
  return { x: event.clientX, y: event.clientY }
}

const startDrag = (mapping, event) => {
  if (!editMode.value || props.kioskMode) return
  dragging.value = true
  dragMapping.value = mapping
  const rect = planContainer.value.getBoundingClientRect()
  const pos = getClientPos(event)
  previewPos.value = { x: pos.x - rect.left, y: pos.y - rect.top }
}

const startTouchDrag = (mapping, event) => {
  if (!editMode.value || props.kioskMode) return
  event.preventDefault()
  startDrag(mapping, event)
}

const onMouseMove = (event) => {
  if (!dragging.value || !dragMapping.value || !planContainer.value) return
  const rect = planContainer.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(rect.width, event.clientX - rect.left))
  const y = Math.max(0, Math.min(rect.height, event.clientY - rect.top))
  previewPos.value = { x, y }
  updateDraggedMapping(x / rect.width, y / rect.height)
}

const onTouchMove = (event) => {
  if (!dragging.value || !dragMapping.value || !planContainer.value) return
  const rect = planContainer.value.getBoundingClientRect()
  const pos = getClientPos(event)
  const x = Math.max(0, Math.min(rect.width, pos.x - rect.left))
  const y = Math.max(0, Math.min(rect.height, pos.y - rect.top))
  previewPos.value = { x, y }
  updateDraggedMapping(x / rect.width, y / rect.height)
}

const updateDraggedMapping = (x, y) => {
  const targetId = dragMapping.value?.entity_id
  if (!targetId) return
  localMappings.value = localMappings.value.map((mapping) =>
    mapping.entity_id === targetId ? { ...mapping, x, y } : mapping
  )
}

const onMouseUp = () => {
  if (!dragging.value) return
  hasChanges.value = true
  dragging.value = false
  dragMapping.value = null
}

const onTouchEnd = () => {
  onMouseUp()
}

const savePositions = () => {
  emit('mapping-update', localMappings.value)
  emit('bg-update', localBgImage.value)
  hasChanges.value = false
}

const onImageUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (loadEvent) => {
    localBgImage.value = loadEvent.target?.result || ''
    hasChanges.value = true
  }
  reader.readAsDataURL(file)
}

watch(
  () => props.entityMapping,
  (value) => {
    if (!hasChanges.value) {
      localMappings.value = [...(value || [])]
    }
  },
  { immediate: true, deep: true }
)

watch(
  () => props.bgImage,
  (value) => {
    if (!hasChanges.value) {
      localBgImage.value = value || ''
    }
  },
  { immediate: true }
)

watch(
  () => props.kioskMode,
  (enabled) => {
    if (enabled) {
      editMode.value = false
      showAddDrawer.value = false
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.glass-effect {
  background: rgba(15, 15, 30, 0.4);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.glow-yellow {
  filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.8));
  animation: glow-pulse-yellow 2s ease-in-out infinite;
}

.glow-blue {
  filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.8));
  animation: glow-pulse-blue 2s ease-in-out infinite;
}

@keyframes glow-pulse-yellow {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(251, 191, 36, 0.5)); }
  50% { filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.9)); }
}

@keyframes glow-pulse-blue {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(34, 211, 238, 0.5)); }
  50% { filter: drop-shadow(0 0 15px rgba(34, 211, 238, 0.9)); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.touch-none {
  touch-action: none;
}
</style>
