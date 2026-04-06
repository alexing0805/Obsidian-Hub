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
 
      <!-- 上传背景图 -->
      <label v-if="editMode"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide text-white/60 border-white/10 cursor-pointer hover:bg-white/10 transition-all">
        UPLOAD MAP
        <input type="file" accept="image/*" class="hidden" @change="onImageUpload" />
      </label>
 
      <!-- 保存位置 -->
      <button v-if="editMode && hasChanges"
        class="glass-panel rounded-xl px-4 py-2 text-[11px] font-bold tracking-wide text-emerald-400 border-emerald-500/50 bg-emerald-500/10 animate-bounce"
        @click="savePositions">
        SAVE CHANGES
      </button>
    </div>
 
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

    <!-- 实体详情弹窗 -->
    <DetailOverlay
      v-if="activeEntity"
      :type="activeEntity.type"
      :ha-entities="haEntities"
      :ma-state="maState"
      :weather-entity-id="weatherEntityId"
      @close="activeEntity = null"
      @toggle-light="$emit('entity-toggle', $event)"
      @climate-action="$emit('climate-action', $event)"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'
import DetailOverlay from './DetailOverlay.vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  entityMapping: { type: Array, default: () => [] },
  bgImage: { type: String, default: '' },  // base64 or URL
  weatherEntityId: { type: String, default: '' },
  maState: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['mapping-update', 'bg-update', 'entity-toggle', 'climate-action'])

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
    activeEntity.value = mapping
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
.entity-icon {
  position: absolute;
  transition: filter 0.2s;
}
.glass-effect {
  background: rgba(20, 20, 40, 0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
