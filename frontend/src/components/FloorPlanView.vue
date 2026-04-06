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
        class="entity-icon absolute flex flex-col items-center cursor-pointer select-none"
        :style="iconStyle(mapping)"
        @click.stop="onIconClick(mapping)"
        @mousedown.stop="startDrag(mapping, $event)"
      >
        <div class="text-2xl leading-none">{{ entityIcon(mapping.type) }}</div>
        <div v-if="showLabels" class="text-xs mt-0.5 px-1 rounded bg-black/50 truncate max-w-[80px] text-center">
          {{ mapping.label || shortId(mapping.entity_id) }}
        </div>
        <!-- 在线状态点 -->
        <div v-if="entityState(mapping.entity_id) === 'on'"
          class="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-yellow-400 shadow-lg shadow-yellow-400/50">
        </div>
      </div>

      <!-- 拖拽预览 -->
      <div
        v-if="dragging"
        class="entity-icon absolute flex flex-col items-center pointer-events-none opacity-70"
        :style="previewStyle"
      >
        <div class="text-2xl leading-none">{{ entityIcon(dragMapping?.type) }}</div>
      </div>
    </div>

    <!-- 右上角控制栏 -->
    <div class="absolute top-3 right-3 flex flex-col gap-2">
      <!-- 编辑模式 -->
      <button
        class="glass-effect rounded-lg px-3 py-1.5 text-xs"
        :class="editMode ? 'text-cyan-400 border border-cyan-500/40' : 'text-white/50 border border-white/10'"
        @click="editMode = !editMode"
      >
        {{ editMode ? '✅ 编辑中' : '✏️ 编辑位置' }}
      </button>

      <!-- 上传背景图 -->
      <label v-if="editMode"
        class="glass-effect rounded-lg px-3 py-1.5 text-xs text-white/70 border border-white/10 cursor-pointer hover:bg-white/5">
        🖼️ 上传底图
        <input type="file" accept="image/*" class="hidden" @change="onImageUpload" />
      </label>

      <!-- 保存位置 -->
      <button v-if="editMode && hasChanges"
        class="glass-effect rounded-lg px-3 py-1.5 text-xs text-emerald-400 border border-emerald-500/40"
        @click="savePositions">
        💾 保存
      </button>

      <!-- 清除底图 -->
      <button v-if="editMode && bgImage"
        class="glass-effect rounded-lg px-3 py-1.5 text-xs text-red-400 border border-red-500/20"
        @click="bgImage = ''; bgImageData = ''; hasChanges = true">
        🗑️ 清除底图
      </button>
    </div>

    <!-- 左上角：图层/模式切换 -->
    <div class="absolute top-3 left-3 flex gap-2 flex-wrap max-w-[60%]">
      <button
        v-for="layer in layers"
        :key="layer"
        class="glass-effect rounded-lg px-2 py-1 text-xs"
        :class="activeLayer === layer ? 'text-cyan-300 border border-cyan-500/40' : 'text-white/40 border border-white/10'"
        @click="activeLayer = layer"
      >
        {{ layer }}
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
import { ref, computed, onMounted, watch } from 'vue'
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

// Layers definition
const layers = ['全部', '客厅', '卧室', '厨房', '卫生间', '阳台']
const activeLayer = ref('全部')

const displayMappings = computed(() => {
  if (activeLayer.value === '全部') return localMappings.value
  return localMappings.value.filter(m => m.layer === activeLayer.value)
})

const entityIcon = (type) => {
  return { '灯': '💡', '空调': '❄️', '开关': '🔌', '传感器': '🌡️', '其他': '📦' }[type] || '📦'
}

const entityState = (entity_id) => {
  const e = props.haEntities.find(e => e.entity_id === entity_id)
  return e?.state || 'off'
}

const shortId = (id) => {
  const parts = id.split('.')
  return parts.length >= 2 ? parts[1].slice(0, 8) : id
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
