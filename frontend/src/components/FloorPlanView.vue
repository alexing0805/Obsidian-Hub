<template>
  <div class="w-full h-full relative overflow-hidden rounded-2xl glass-effect">

    <!-- 背景图片 + 实体图标层 -->
    <div
      ref="planContainer"
      class="w-full h-full"
      :style="bgStyle"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
    >
      <!-- 实体图标 -->
      <div
        v-for="mapping in displayMappings"
        :key="mapping.entity_id"
        class="entity-item absolute flex flex-col items-center cursor-pointer select-none group"
        :style="iconStyle(mapping)"
        @click.stop="onIconClick(mapping)"
        @mousedown.stop="startDrag(mapping, $event)"
      >
        <!-- 光晕效果 (仅灯光开启时) -->
        <div v-if="entityState(mapping.entity_id) === 'on' && mapping.type === '灯'" 
          class="absolute inset-0 -m-8 rounded-full bg-yellow-400/20 blur-2xl animate-pulse"></div>
        
        <!-- 图标容器 -->
        <div class="relative w-12 h-12 flex items-center justify-center rounded-2xl glass-panel transition-all duration-300 group-hover:scale-110 group-hover:bg-white/10"
          :class="entityState(mapping.entity_id) === 'on' ? 'ring-2 ring-white/20' : 'ring-1 ring-white/5'">
          <component :is="getIconComponent(mapping.type)" 
            class="w-6 h-6 transition-colors duration-300"
            :class="entityState(mapping.entity_id) === 'on' ? (mapping.type === '灯' ? 'text-yellow-300 glow-yellow' : 'text-cyan-300 glow-blue') : 'text-white/40'" />
          
          <!-- 状态呼吸灯 -->
          <div v-if="entityState(mapping.entity_id) === 'on'"
            class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)] bg-white animate-pulse">
          </div>
        </div>

        <div v-if="showLabels" class="mt-2 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-md border border-white/5 text-[10px] font-bold tracking-tight text-white/80 whitespace-nowrap overflow-hidden text-ellipsis max-w-[100px] shadow-sm">
          {{ mapping.label || shortId(mapping.entity_id) }}
        </div>
      </div>
 
      <!-- 拖拽预览 -->
      <div
        v-if="dragging"
        class="entity-item absolute flex flex-col items-center pointer-events-none opacity-50"
        :style="previewStyle"
      >
        <div class="w-12 h-12 flex items-center justify-center rounded-2xl glass-panel border-dashed border-cyan-400/50">
          <component :is="getIconComponent(dragMapping?.type)" class="w-6 h-6 text-cyan-400" />
        </div>
      </div>
    </div>
 
    <!-- 右上角控制栏 -->
    <div class="absolute top-4 right-4 flex flex-col gap-2.5">
      <!-- 编辑模式 -->
      <button
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide transition-all active:scale-95"
        :class="editMode ? 'text-cyan-300 border-cyan-500/50 bg-cyan-500/10' : 'text-white/40 border-white/10 hover:bg-white/5'"
        @click="editMode = !editMode"
      >
        {{ editMode ? 'DONE' : 'EDIT PLAN' }}
      </button>
 
      <!-- 添加设备 -->
      <button v-if="editMode"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10 transition-all"
        @click="showAddDrawer = true">
        ADD DEVICE
      </button>

      <!-- 上传背景图 -->
      <label v-if="editMode"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide text-white/60 border-white/10 cursor-pointer hover:bg-white/10 transition-all">
        UPLOAD MAP
        <input type="file" accept="image/*" class="hidden" @change="onImageUpload" />
      </label>
 
      <!-- 保存位置 -->
      <button v-if="editMode && hasChanges"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide text-emerald-400 border-emerald-500/50 bg-emerald-500/10 animate-pulse"
        @click="savePositions">
        SAVE CHANGES
      </button>
    </div>
 
    <!-- 添加设备抽屉 (Modal) -->
    <Teleport to="body">
      <div v-if="showAddDrawer" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-xl" @click="showAddDrawer = false"></div>
        <div class="relative glass-panel rounded-[2.5rem] w-full max-w-xl max-h-[80vh] flex flex-col overflow-hidden shadow-2xl border-white/10 flex flex-col animate-fade-in">
          <div class="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-xl font-heading font-extrabold text-white">Add Device to Plan</h3>
            <button class="text-white/20 hover:text-white" @click="showAddDrawer = false">✕</button>
          </div>
          
          <div class="p-4 border-b border-white/5">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search entities (e.g. light.kitchen)" 
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
            />
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-2">
            <div 
              v-for="entity in availableEntities" 
              :key="entity.entity_id"
              class="flex items-center justify-between p-4 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-all group"
              @click="addEntityToPlan(entity)"
            >
              <div class="flex flex-col min-w-0">
                <span class="text-sm font-bold text-white truncate">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                <span class="text-[10px] uppercase tracking-tighter text-white/30 truncate">{{ entity.entity_id }}</span>
              </div>
              <button class="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 text-[10px] font-black uppercase opacity-0 group-hover:opacity-100 transition-opacity">
                Select
              </button>
            </div>
            <div v-if="availableEntities.length === 0" class="text-center py-20 text-white/20">
               No entities found
            </div>
          </div>
        </div>
      </div>
    </Teleport>
 
    <!-- 左上角：图层/模式切换 -->
    <div class="absolute top-4 left-4 flex gap-2 flex-wrap max-w-[70%]">
      <button
        v-for="layer in layers"
        :key="layer"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wider transition-all"
        :class="activeLayer === layer ? 'text-white border-white/30 bg-white/10 shadow-lg' : 'text-white/30 border-white/5 hover:bg-white/5 hover:text-white/60'"
        @click="activeLayer = layer"
      >
        {{ layer.toUpperCase() }}
      </button>
    </div>

    <!-- 编辑模式提示 -->
    <div v-if="editMode" class="absolute bottom-3 left-1/2 -translate-x-1/2 glass-effect rounded-lg px-4 py-1.5 text-xs text-white/50">
      💡 点击图标切换开关 | 拖拽移动位置 | 🖼️ 上传户型图
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  entityMapping: { type: Array, default: () => [] },
  bgImage: { type: String, default: '' },  // base64 or URL
  weatherEntityId: { type: String, default: '' },
  maState: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['mapping-update', 'bg-update', 'entity-toggle', 'climate-action', 'open'])

const planContainer = ref(null)
const editMode = ref(false)
const dragging = ref(false)
const dragMapping = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const previewPos = ref({ x: 0, y: 0 })
const activeEntity = ref(null)
const localMappings = ref([])
const localBgImage = ref('')
const hasChanges = ref(false)
const showAddDrawer = ref(false)
const searchQuery = ref('')
 
const availableEntities = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const mappedIds = localMappings.value.map(m => m.entity_id)
  return props.haEntities.filter(e => {
    const isMapped = mappedIds.includes(e.entity_id)
    if (isMapped) return false
    const name = (e.attributes?.friendly_name || '').toLowerCase()
    const id = e.entity_id.toLowerCase()
    return name.includes(query) || id.includes(query)
  }).slice(0, 50)
})

const addEntityToPlan = (entity) => {
  const type = entity.entity_id.startsWith('light.') ? '灯' : 
               entity.entity_id.startsWith('climate.') ? '空调' : 
               entity.entity_id.startsWith('switch.') ? '开关' :
               entity.entity_id.startsWith('sensor.') ? '传感器' : '其他'
  
  const newMapping = {
    entity_id: entity.entity_id,
    x: 0.5,
    y: 0.5,
    type,
    label: entity.attributes?.friendly_name || entity.entity_id,
    layer: activeLayer.value === '全部' ? '客厅' : activeLayer.value
  }
  
  localMappings.value = [...localMappings.value, newMapping]
  hasChanges.value = true
  showAddDrawer.value = false
  searchQuery.value = ''
}

const layers = ['全部', '客厅', '卧室', '厨房', '卫生间', '阳台']
const activeLayer = ref('全部')
const displayMappings = computed(() => {
  if (activeLayer.value === '全部') return localMappings.value
  return localMappings.value.filter(m => m.layer === activeLayer.value)
})

// 现代图标组件 (使用 h() 渲染函数以兼容生产构建)
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
const IconOther = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { d: 'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z' }),
  h('path', { d: 'm3.3 7 8.7 5 8.7-5M12 22V12' })
])

const getIconComponent = (type) => {
  return { '灯': IconLight, '空调': IconClimate, '开关': IconSwitch, '传感器': IconSensor }[type] || IconOther
}

const entityState = (entity_id) => {
  const e = props.haEntities.find(e => e.entity_id === entity_id)
  return e?.state || 'off'
}

const shortId = (id) => {
  const parts = id.split('.')
  return parts.length >= 2 ? parts[1].toUpperCase() : id
}

const bgStyle = computed(() => {
  if (localBgImage.value) {
    return {
      backgroundImage: `url(${localBgImage.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  }
  return {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
  }
})

const iconStyle = (mapping) => {
  const x = (mapping.x || 0.5) * 100
  const y = (mapping.y || 0.5) * 100
  const state = entityState(mapping.entity_id)
  const isActive = state === 'on'
  const isComplex = ['空调', '传感器'].includes(mapping.type)
  const color = isActive
    ? (mapping.type === '灯' ? '#fbbf24' : '#60a5fa')
    : '#555'
  return {
    left: `${x}%`,
    top: `${y}%`,
    transform: 'translate(-50%, -50%)',
    color,
    filter: isActive && mapping.type === '灯' ? 'drop-shadow(0 0 6px #fbbf2488)' : 'none',
    zIndex: isActive ? 5 : 4,
  }
}

const previewStyle = computed(() => ({
  left: `${previewPos.value.x}px`,
  top: `${previewPos.value.y}px`,
  transform: 'translate(-50%, -50%)',
  color: '#60a5fa',
}))

const onIconClick = (mapping) => {
  if (editMode.value) return
  if (['空调', '传感器'].includes(mapping.type)) {
    emit('open', mapping.type === '空调' ? 'climate' : 'sensor')
  } else {
    // Toggle directly
    const entity = props.haEntities.find(e => e.entity_id === mapping.entity_id)
    emit('entity-toggle', entity || mapping)
  }
}

const onIconClick2 = (mapping) => {
  if (editMode.value) return
  const entity = props.haEntities.find(e => e.entity_id === mapping.entity_id)
  if (['空调', '传感器'].includes(mapping.type)) {
    activeEntity.value = mapping
  } else {
    emit('entity-toggle', entity || mapping)
  }
}

const startDrag = (mapping, event) => {
  if (!editMode.value) return
  dragging.value = true
  dragMapping.value = mapping
  const rect = planContainer.value.getBoundingClientRect()
  const x = (mapping.x || 0.5) * rect.width
  const y = (mapping.y || 0.5) * rect.height
  dragOffset.value = {
    x: event.clientX - x,
    y: event.clientY - y,
  }
  previewPos.value = { x: event.clientX - rect.left, y: event.clientY - rect.top }
}

const onMouseDown = (e) => {
  if (!editMode.value || dragging.value) return
}

const onMouseMove = (e) => {
  if (!dragging.value || !dragMapping.value || !planContainer.value) return
  const rect = planContainer.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(rect.width, e.clientX - rect.left - dragOffset.value.x + dragOffset.value.x))
  const y = Math.max(0, Math.min(rect.height, e.clientY - rect.top - dragOffset.value.y + dragOffset.value.y))
  previewPos.value = { x, y }

  // Update position in real-time
  const nx = x / rect.width
  const ny = y / rect.height
  const idx = localMappings.value.findIndex(m => m.entity_id === dragMapping.value.entity_id)
  if (idx !== -1) {
    localMappings.value = localMappings.value.map((m, i) =>
      i === idx ? { ...m, x: nx, y: ny } : m
    )
  }
}

const onMouseUp = () => {
  if (dragging.value) {
    hasChanges.value = true
    dragging.value = false
    dragMapping.value = null
  }
}

const savePositions = () => {
  emit('mapping-update', localMappings.value)
  emit('bg-update', localBgImage.value)
  hasChanges.value = false
}

const onImageUpload = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    localBgImage.value = ev.target.result
    hasChanges.value = true
  }
  reader.readAsDataURL(file)
}

const showLabels = computed(() => {
  return editMode.value || activeLayer.value !== '全部'
})

// Sync from props
watch(() => props.entityMapping, (v) => {
  if (!hasChanges.value) localMappings.value = [...(v || [])]
}, { immediate: true, deep: true })

watch(() => props.bgImage, (v) => {
  if (!hasChanges.value) localBgImage.value = v || ''
}, { immediate: true })
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
 
@keyframes music-bar {
  0%, 100% { height: 4px; }
  50% { height: 100%; }
}
 
.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
 
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
