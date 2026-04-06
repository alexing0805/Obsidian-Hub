<template>
  <div class="flex flex-col h-full">

    <!-- 时钟 -->
    <div class="p-4 border-b border-white/10 shrink-0">
      <div class="text-center">
        <div class="text-3xl font-light tracking-wider">{{ currentTime }}</div>
        <div class="text-xs text-white/40 mt-1">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 控件区域（可滚动） -->
    <div class="flex-1 overflow-y-auto p-4 space-y-2">

      <!-- 天气 -->
      <div v-if="widgets.weather" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'weather')">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl">{{ weatherEmoji }}</span>
            <div>
              <div class="text-sm font-medium">{{ weatherTemperature }}</div>
              <div class="text-xs text-white/40">{{ weatherText }}</div>
            </div>
          </div>
          <span class="text-xs text-white/30">→</span>
        </div>
      </div>

      <!-- 统计一行 -->
      <div v-if="widgets.stats" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'overview')">
        <div class="grid grid-cols-4 gap-1 text-center">
          <div>
            <div class="text-lg font-bold text-yellow-300">{{ summary.lights_on }}</div>
            <div class="text-xs text-white/30">亮灯</div>
          </div>
          <div>
            <div class="text-lg font-bold text-blue-300">{{ summary.climate_total }}</div>
            <div class="text-xs text-white/30">空调</div>
          </div>
          <div>
            <div class="text-lg font-bold text-red-300">{{ summary.low_battery_count }}</div>
            <div class="text-xs text-white/30">低电量</div>
          </div>
          <div>
            <div class="text-lg font-bold text-orange-300">{{ summary.offline_count }}</div>
            <div class="text-xs text-white/30">离线</div>
          </div>
        </div>
      </div>

      <!-- 灯光 -->
      <div v-if="widgets.lights" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'lights')">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">💡</span>
            <span class="text-sm">灯光 <span class="text-yellow-300 font-bold">{{ summary.lights_on }}</span> / {{ summary.lights_total }}</span>
          </div>
          <span class="text-xs text-white/30">→</span>
        </div>
        <div v-if="topLights.length" class="mt-2 space-y-1">
          <div v-for="light in topLights.slice(0,3)" :key="light.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/50 truncate">{{ light.attributes?.friendly_name || light.entity_id }}</span>
            <span :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
              {{ light.state === 'on' ? '●' : '○' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 空调 -->
      <div v-if="widgets.climate" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'climate')">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">❄️</span>
            <span class="text-sm">空调 <span class="text-blue-300 font-bold">{{ summary.climate_total }}</span> 台</span>
          </div>
          <span class="text-xs text-white/30">→</span>
        </div>
        <div v-if="topClimates.length" class="mt-2 space-y-1">
          <div v-for="c in topClimates.slice(0,2)" :key="c.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/50 truncate">{{ c.attributes?.friendly_name || c.entity_id }}</span>
            <span class="text-blue-300">{{ c.attributes?.temperature || '--' }}°</span>
          </div>
        </div>
      </div>

      <!-- 低电量 -->
      <div v-if="widgets.battery" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'battery')">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">🔋</span>
            <span class="text-sm">低电量</span>
          </div>
          <span class="text-xs px-2 py-0.5 rounded font-bold"
            :class="lowBatteryEntities.length ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'">
            {{ lowBatteryEntities.length }} 个
          </span>
        </div>
      </div>

      <!-- 离线设备 -->
      <div v-if="widgets.offline" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'offline')">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">📡</span>
            <span class="text-sm">离线设备</span>
          </div>
          <span class="text-xs px-2 py-0.5 rounded font-bold"
            :class="offlineEntities.length ? 'bg-orange-500/20 text-orange-400' : 'bg-emerald-500/20 text-emerald-400'">
            {{ offlineEntities.length }} 个
          </span>
        </div>
      </div>

      <!-- 音乐 -->
      <div v-if="widgets.music" class="glass-effect rounded-xl cursor-pointer card-hover transition-colors"
        @click="$emit('set-view', 'music')">
        <MusicAssistantPlayer :ma-state="maState" class="p-3" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  maState: { type: Object, default: () => ({}) },
  currentTime: { type: String, default: '' },
  currentDate: { type: String, default: '' },
  weatherEntityId: { type: String, default: '' },
  sidebarWidgets: { type: Object, default: () => ({}) },
})

defineEmits(['set-view'])

const widgets = computed(() => ({
  weather: props.sidebarWidgets.weather !== false,
  stats: props.sidebarWidgets.stats !== false,
  lights: props.sidebarWidgets.lights !== false,
  climate: props.sidebarWidgets.climate !== false,
  battery: props.sidebarWidgets.battery !== false,
  offline: props.sidebarWidgets.offline !== false,
  music: props.sidebarWidgets.music !== false,
}))

const weatherEntity = computed(() =>
  props.haEntities.find(e => e.entity_id === props.weatherEntityId) ||
  props.haEntities.find(e => e.entity_id.startsWith('weather.')) || null
)
const weatherText = computed(() => weatherEntity.value?.state || '未知')
const weatherTemperature = computed(() => {
  const v = weatherEntity.value?.attributes?.temperature
  return v !== undefined && v !== null ? `${Number(v).toFixed(1)}°` : '--'
})
const weatherEmoji = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  return '🌤️'
})

const topLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')))
const topClimates = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('climate.')))
const lowBatteryEntities = computed(() =>
  props.haEntities.filter(e => {
    const a = e.attributes || {}
    if (a.device_class !== 'battery') return false
    const v = parseFloat(e.state)
    return !isNaN(v) && v <= 20
  })
)
const offlineEntities = computed(() =>
  props.haEntities.filter(e => ['unknown', 'unavailable', 'none', ''].includes(String(e.state).toLowerCase()))
)
</script>
