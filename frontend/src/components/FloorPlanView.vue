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
        class="entity-item absolute flex flex-col items-center select-none group overflow-visible"
        :class="mapping.isClickable ? 'cursor-pointer' : 'cursor-default'"
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
          v-if="mapping.displayMode === 'metric'"
          class="metric-card glass-panel"
          :class="[mapping.panelClass, mapping.metricCardClass]"
        >
          <div class="metric-reading">
            <span class="metric-value">{{ mapping.metricValue }}</span>
            <span class="metric-unit">{{ mapping.metricUnit }}</span>
          </div>
          <div class="metric-label">{{ mapping.metricLabel }}</div>
        </div>

        <div
          v-else
          class="relative w-16 h-16 flex items-center justify-center rounded-2xl glass-panel overflow-visible transition-all duration-300 group-hover:scale-110 group-hover:bg-white/10"
          :class="mapping.panelClass"
        >
          <component
            :is="mapping.iconComponent"
            class="w-8 h-8 transition-colors duration-300"
            :class="mapping.iconClass"
          />

          <div
            v-if="mapping.badgeValue"
            class="absolute top-1 right-1 px-1.5 py-0.5 bg-cyan-500 text-[10px] font-black text-white rounded-full shadow-lg border border-white/20 select-none z-10 leading-none"
          >
            {{ mapping.badgeValue }}
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
          <component :is="resolveEntityIcon(dragMapping?.entity, dragMapping)" class="w-8 h-8 text-cyan-400" />
        </div>
      </div>
    </div>

    <template v-if="!kioskMode">
      <div class="absolute bottom-28 right-6 flex flex-col gap-3 z-40">
        <button
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all shadow-lg"
          :class="editMode ? 'text-cyan-300 border border-cyan-500/50 bg-cyan-500/10' : 'border-white/10'"
          @click="editMode = !editMode"
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </button>

        <button
          v-if="editMode"
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/10 transition-all shadow-lg"
          @click="showAddDrawer = true"
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
        </button>

        <label
          v-if="editMode"
          class="w-14 h-14 rounded-2xl glass-panel flex items-center justify-center text-white/60 border border-white/10 hover:bg-white/10 hover:text-white/80 transition-all shadow-lg cursor-pointer"
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
        >
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </button>
      </div>

      <div v-if="editMode" class="absolute top-4 left-4 flex gap-2 flex-wrap max-w-[60%]">
        <button
          v-for="layer in layers"
          :key="layer.id"
          class="glass-panel rounded-xl px-4 py-2.5 text-sm font-bold tracking-wider transition-all"
          :class="activeLayer === layer.id ? 'text-white border-white/30 bg-white/10 shadow-lg' : 'text-white/40 border-white/5 hover:bg-white/5 hover:text-white/60'"
          @click="activeLayer = layer.id"
        >
          {{ layer.label }}
        </button>
      </div>
    </template>

    <Teleport to="body">
      <div v-if="showAddDrawer" class="fixed inset-0 z-[100] flex items-center justify-center p-8">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-xl" @click="showAddDrawer = false"></div>
        <div class="relative glass-panel rounded-[2.5rem] w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden shadow-2xl border-white/10 animate-fade-in">
          <div class="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-xl font-heading font-extrabold text-white">添加实体到户型图</h3>
            <button class="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all bg-white/5 border border-white/10" @click="showAddDrawer = false">×</button>
          </div>

          <div class="p-4 border-b border-white/5">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索设备，例如 light.kitchen"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-base text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
            />
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-2">
            <div
              v-for="entity in availableEntities"
              :key="entity.entity_id"
              class="flex items-center justify-between p-5 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-all group"
              @click="addEntityToPlan(entity)"
            >
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <component :is="resolveEntityIcon(entity, { type: getEntityType(entity.entity_id), icon_variant: defaultIconVariant(entity) })" class="w-5 h-5 text-white/55 shrink-0" />
                <div class="flex flex-col min-w-0 flex-1">
                  <span class="text-base font-bold text-white truncate">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                  <span class="text-xs uppercase tracking-tighter text-white/30 truncate">{{ entity.entity_id }}</span>
                </div>
              </div>
              <button class="px-4 py-2 rounded-xl bg-cyan-500/20 text-cyan-400 text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity border border-cyan-500/30">
                添加
              </button>
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

const layers = [
  { id: 'All', label: '全部' },
  { id: 'Living', label: '客厅' },
  { id: 'Bedroom', label: '卧室' },
  { id: 'Kitchen', label: '厨房' },
  { id: 'Bath', label: '卫生间' },
  { id: 'Balcony', label: '阳台' }
]

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
const activeLayer = ref('All')

const entitiesById = computed(() => {
  const map = new Map()
  for (const entity of props.haEntities) map.set(entity.entity_id, entity)
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
  }).slice(0, 60)
})

const parseMetricValue = (entity) => {
  const raw = Number.parseFloat(entity?.state)
  if (!Number.isFinite(raw)) return null
  return Math.round(raw)
}

const getSensorDisplayMode = (entity) => {
  const unit = String(entity?.attributes?.unit_of_measurement || '').toLowerCase()
  const deviceClass = String(entity?.attributes?.device_class || '').toLowerCase()
  if (deviceClass === 'temperature' || unit.includes('c') || unit.includes('f')) return 'metric'
  if (deviceClass === 'humidity' || unit === '%' || unit.includes('%')) return 'metric'
  return 'default'
}

const getMetricMeta = (entity) => {
  const deviceClass = String(entity?.attributes?.device_class || '').toLowerCase()
  if (deviceClass === 'humidity') return { unit: '%', className: 'metric-humidity', label: 'Humidity' }
  return { unit: '°', className: 'metric-temperature', label: 'Temp' }
}

const defaultIconVariant = (entity) => {
  if (!entity?.entity_id?.startsWith('light.')) return ''
  return 'bulb'
}

const iconBaseProps = { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.9', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }
const IconLightBulb = () => h('svg', iconBaseProps, [h('path', { d: 'M9 18h6' }), h('path', { d: 'M10 22h4' }), h('path', { d: 'M8.5 10a3.5 3.5 0 1 1 7 0c0 1.35-.47 2.18-1.55 3.2-.63.6-1.02 1.15-1.2 1.8h-1.5c-.18-.65-.57-1.2-1.2-1.8C8.97 12.18 8.5 11.35 8.5 10Z' })])
const IconClimateCool = () => h('svg', iconBaseProps, [h('path', { d: 'M12 3v18' }), h('path', { d: 'm7 6 5 3 5-3' }), h('path', { d: 'm7 18 5-3 5 3' }), h('path', { d: 'M4 12h16' })])
const IconClimateHeat = () => h('svg', iconBaseProps, [h('path', { d: 'M12 3c2.6 3 4 5.1 4 7.1A4 4 0 1 1 8 10.1C8 8.1 9.4 6 12 3Z' })])
const IconClimateDry = () => h('svg', iconBaseProps, [h('path', { d: 'M12 4c3 3.6 5 6 5 8.2A5 5 0 1 1 7 12.2C7 10 9 7.6 12 4Z' })])
const IconClimateFan = () => h('svg', iconBaseProps, [h('circle', { cx: '12', cy: '12', r: '2' }), h('path', { d: 'M12 4c2 0 3 1 3 3 0 1.5-1 3-3 5-2-2-3-3.5-3-5 0-2 1-3 3-3Z' })])
const IconClimateAuto = () => h('svg', iconBaseProps, [h('circle', { cx: '12', cy: '12', r: '6' }), h('path', { d: 'M12 6v12' }), h('path', { d: 'M6 12h12' })])
const IconClimateOff = () => h('svg', iconBaseProps, [h('path', { d: 'M12 3v7' }), h('path', { d: 'M8.2 5.8a7 7 0 1 0 7.6 0' })])
const IconSwitch = () => h('svg', iconBaseProps, [h('rect', { x: '5', y: '5', width: '14', height: '14', rx: '3' }), h('path', { d: 'M12 8v8' })])
const IconSensor = () => h('svg', iconBaseProps, [h('circle', { cx: '12', cy: '12', r: '3' }), h('path', { d: 'M12 2v2M12 20v2M2 12h2M20 12h2' })])
const IconCover = () => h('svg', iconBaseProps, [h('rect', { x: '4', y: '5', width: '16', height: '14', rx: '2' }), h('path', { d: 'M8 5v14M12 5v14M16 5v14' })])
const IconFan = () => h('svg', iconBaseProps, [h('circle', { cx: '12', cy: '12', r: '2' }), h('path', { d: 'M12 4c2 0 3 1 3 3 0 1.5-1 3-3 5-2-2-3-3.5-3-5 0-2 1-3 3-3Z' })])
const IconMedia = () => h('svg', iconBaseProps, [h('rect', { x: '3', y: '6', width: '18', height: '12', rx: '2' }), h('path', { d: 'm10 9 5 3-5 3z' })])
const IconOther = () => h('svg', iconBaseProps, [h('path', { d: 'M12 3 4 7.5v9L12 21l8-4.5v-9Z' })])

const getClimateIcon = (entity) => {
  const state = String(entity?.state || '').toLowerCase()
  if (state === 'heat') return IconClimateHeat
  if (state === 'dry') return IconClimateDry
  if (state === 'fan_only') return IconClimateFan
  if (state === 'auto') return IconClimateAuto
  if (state === 'off') return IconClimateOff
  return IconClimateCool
}

const resolveEntityIcon = (entity, mapping = {}) => {
  const entityId = entity?.entity_id || mapping?.entity_id || ''
  if (entityId.startsWith('light.')) return IconLightBulb
  if (entityId.startsWith('climate.')) return getClimateIcon(entity)
  if (entityId.startsWith('cover.')) return IconCover
  if (entityId.startsWith('fan.')) return IconFan
  if (entityId.startsWith('media_player.')) return IconMedia
  if (entityId.startsWith('switch.')) return IconSwitch
  if (entityId.startsWith('sensor.') || entityId.startsWith('binary_sensor.')) return IconSensor
  return IconOther
}

const getEntityType = (entityId) => {
  if (entityId.startsWith('light.')) return 'light'
  if (entityId.startsWith('climate.')) return 'climate'
  if (entityId.startsWith('switch.')) return 'switch'
  if (entityId.startsWith('sensor.') || entityId.startsWith('binary_sensor.')) return 'sensor'
  if (entityId.startsWith('cover.')) return 'cover'
  if (entityId.startsWith('fan.')) return 'fan'
  if (entityId.startsWith('media_player.')) return 'media'
  return 'other'
}

const getDisplayMode = (entity, mapping) => {
  if (!entity) return 'icon'
  if (mapping?.type === 'sensor' && getSensorDisplayMode(entity) === 'metric') return 'metric'
  return 'icon'
}

const getEntityBadgeValue = (entity) => {
  if (!entity) return null
  if (entity.entity_id.startsWith('climate.')) {
    const value = entity.attributes?.temperature ?? entity.attributes?.current_temperature
    return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : null
  }
  if (entity.entity_id.startsWith('cover.')) {
    const position = Number(entity.attributes?.current_position)
    return Number.isFinite(position) ? `${position}%` : null
  }
  if (entity.entity_id.startsWith('light.') && entity.state === 'on') {
    const brightness = entity.attributes?.brightness
    if (brightness) return `${Math.round((brightness / 255) * 100)}%`
  }
  return null
}

const isEntityActive = (entity) => {
  if (!entity) return false
  const state = String(entity.state).toLowerCase()
  if (entity.entity_id.startsWith('climate.')) return state !== 'off'
  if (entity.entity_id.startsWith('cover.')) return state === 'open'
  return state === 'on'
}

const activeColorClass = (type, entity) => {
  if (type === 'light') return 'text-yellow-300 glow-yellow'
  if (type === 'climate') {
    const state = String(entity?.state || '').toLowerCase()
    if (state === 'heat') return 'text-orange-300 glow-warm'
    return 'text-cyan-300 glow-blue'
  }
  if (type === 'cover') return 'text-blue-300 glow-blue'
  if (type === 'fan') return 'text-sky-300 glow-blue'
  if (type === 'media') return 'text-fuchsia-300 glow-violet'
  return 'text-cyan-300 glow-blue'
}

const displayMappings = computed(() => {
  const baseMappings = activeLayer.value === 'All'
    ? localMappings.value
    : localMappings.value.filter((mapping) => mapping.layer === activeLayer.value)

  return baseMappings.map((mapping) => {
    const entity = entitiesById.value.get(mapping.entity_id)
    const active = isEntityActive(entity)
    const displayMode = getDisplayMode(entity, mapping)
    const metricMeta = displayMode === 'metric' ? getMetricMeta(entity) : null
    const metricValue = displayMode === 'metric' ? parseMetricValue(entity) : null

    return {
      ...mapping,
      entity,
      displayMode,
      isClickable: displayMode !== 'metric',
      metricValue: metricValue ?? '--',
      metricUnit: metricMeta?.unit || '',
      metricLabel: metricMeta?.label || '',
      metricCardClass: metricMeta?.className || '',
      badgeValue: displayMode === 'metric' ? null : getEntityBadgeValue(entity),
      iconComponent: resolveEntityIcon(entity, mapping),
      showGlow: !props.kioskMode && active && mapping.type === 'light',
      showIndicator: !props.kioskMode && active && mapping.type === 'light',
      panelClass: active ? 'ring-2 ring-white/20' : 'ring-1 ring-white/5',
      iconClass: active ? activeColorClass(mapping.type, entity) : 'text-white/40',
      style: {
        left: `${(mapping.x || 0.5) * 100}%`,
        top: `${(mapping.y || 0.5) * 100}%`,
        transform: 'translate(-50%, -50%)',
        zIndex: active ? 5 : 4
      }
    }
  })
})

const showLabels = computed(() => editMode.value || activeLayer.value !== 'All')

const bgStyle = computed(() => localBgImage.value ? {
  backgroundImage: `url(${localBgImage.value})`,
  backgroundSize: 'contain',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat'
} : {
  background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
})

const previewStyle = computed(() => ({
  left: `${previewPos.value.x}px`,
  top: `${previewPos.value.y}px`,
  transform: 'translate(-50%, -50%)',
  color: '#60a5fa'
}))

const addEntityToPlan = (entity) => {
  localMappings.value = [...localMappings.value, {
    entity_id: entity.entity_id,
    x: 0.5,
    y: 0.5,
    type: getEntityType(entity.entity_id),
    label: entity.attributes?.friendly_name || entity.entity_id,
    layer: activeLayer.value === 'All' ? 'Living' : activeLayer.value,
    icon_variant: defaultIconVariant(entity)
  }]
  hasChanges.value = true
  showAddDrawer.value = false
  searchQuery.value = ''
}

const shortId = (id) => {
  const parts = id.split('.')
  return parts.length >= 2 ? parts[1].toUpperCase() : id
}

const onIconClick = (mapping) => {
  if (editMode.value || !mapping.isClickable) return
  const entityId = mapping.entity_id
  if (entityId.startsWith('cover.')) return emit('open', { type: 'cover', entityId })
  if (entityId.startsWith('climate.')) return emit('open', { type: 'climate', entityId })
  if (entityId.startsWith('sensor.') || entityId.startsWith('binary_sensor.')) return
  emit('entity-toggle', mapping.entity || mapping)
}

const getClientPos = (event) => {
  if (event.touches && event.touches.length > 0) return { x: event.touches[0].clientX, y: event.touches[0].clientY }
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
  localMappings.value = localMappings.value.map((mapping) => mapping.entity_id === targetId ? { ...mapping, x, y } : mapping)
}

const onMouseUp = () => {
  if (!dragging.value) return
  hasChanges.value = true
  dragging.value = false
  dragMapping.value = null
}

const onTouchEnd = () => onMouseUp()

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

watch(() => props.entityMapping, (value) => {
  if (!hasChanges.value) localMappings.value = [...(value || [])]
}, { immediate: true, deep: true })

watch(() => props.bgImage, (value) => {
  if (!hasChanges.value) localBgImage.value = value || ''
}, { immediate: true })

watch(() => props.kioskMode, (enabled) => {
  if (enabled) {
    editMode.value = false
    showAddDrawer.value = false
  }
}, { immediate: true })
</script>

<style scoped>
.glass-effect {
  background: rgba(15, 15, 30, 0.4);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.metric-card {
  width: 5.5rem;
  min-height: 4.9rem;
  border-radius: 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.28rem;
  padding: 0.55rem 0.45rem 0.5rem;
  background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(255,255,255,0.05));
}

.metric-reading {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0.08rem;
  line-height: 1;
}

.metric-value {
  font-size: 2rem;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.05em;
  color: #f8fafc;
}

.metric-unit {
  font-size: 0.9rem;
  line-height: 1;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.66);
  margin-top: 0.2rem;
}

.metric-label {
  font-size: 0.52rem;
  line-height: 1;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.34);
}

.metric-temperature {
  border-color: rgba(34, 211, 238, 0.28);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 10px 30px rgba(6, 182, 212, 0.12);
}

.metric-humidity {
  border-color: rgba(96, 165, 250, 0.28);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 10px 30px rgba(59, 130, 246, 0.12);
}

.glow-yellow { filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.8)); animation: glow-pulse-yellow 2s ease-in-out infinite; }
.glow-blue { filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.8)); animation: glow-pulse-blue 2s ease-in-out infinite; }
.glow-warm { filter: drop-shadow(0 0 8px rgba(251, 146, 60, 0.85)); animation: glow-pulse-warm 2s ease-in-out infinite; }
.glow-violet { filter: drop-shadow(0 0 8px rgba(217, 70, 239, 0.8)); animation: glow-pulse-violet 2s ease-in-out infinite; }
@keyframes glow-pulse-yellow { 0%,100% { filter: drop-shadow(0 0 5px rgba(251,191,36,.5)); } 50% { filter: drop-shadow(0 0 15px rgba(251,191,36,.9)); } }
@keyframes glow-pulse-blue { 0%,100% { filter: drop-shadow(0 0 5px rgba(34,211,238,.5)); } 50% { filter: drop-shadow(0 0 15px rgba(34,211,238,.9)); } }
@keyframes glow-pulse-warm { 0%,100% { filter: drop-shadow(0 0 5px rgba(251,146,60,.45)); } 50% { filter: drop-shadow(0 0 15px rgba(251,146,60,.9)); } }
@keyframes glow-pulse-violet { 0%,100% { filter: drop-shadow(0 0 5px rgba(217,70,239,.45)); } 50% { filter: drop-shadow(0 0 15px rgba(217,70,239,.85)); } }

.animate-fade-in { animation: fade-in 0.3s ease-out; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.touch-none { touch-action: none; }
</style>
