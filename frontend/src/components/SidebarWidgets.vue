<template>
  <div class="flex flex-col h-full">

    <!-- 时钟 -->
    <div class="p-4 border-b border-white/10 shrink-0">
      <div class="text-center">
        <div class="text-3xl font-light tracking-wider">{{ currentTime }}</div>
        <div class="text-xs text-white/40 mt-1">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 控件列表 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-2">

      <!-- 天气 -->
      <div v-if="widgets.weather && weatherEntity" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('open', 'weather')">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl">{{ weatherEmoji }}</span>
            <div>
              <div class="text-sm font-medium">{{ weatherTemperature }}</div>
              <div class="text-xs text-white/40">{{ weatherText }}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-xs text-white/30">点击详情 →</div>
          </div>
        </div>
        <div class="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
          <div class="bg-white/5 rounded-lg py-1 px-2">
            <div class="text-white/40">湿度</div>
            <div class="text-white/70">{{ weatherHumidity }}</div>
          </div>
          <div class="bg-white/5 rounded-lg py-1 px-2">
            <div class="text-white/40">降水量</div>
            <div class="text-white/70">{{ weatherPrecipitation }}</div>
          </div>
          <div class="bg-white/5 rounded-lg py-1 px-2">
            <div class="text-white/40">风力</div>
            <div class="text-white/70">{{ weatherWind || '--' }}</div>
          </div>
        </div>
      </div>

      <!-- 统计一行 -->
      <div v-if="widgets.stats" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('open', 'stats')">
        <div class="text-xs text-white/30 mb-2">统计概览</div>
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
        @click="$emit('open', 'lights')">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium">💡 灯光</span>
          <span class="text-xs text-yellow-300 font-bold">{{ summary.lights_on }} / {{ summary.lights_total }}</span>
        </div>
        <div v-if="topLights.length" class="space-y-1">
          <div v-for="light in topLights" :key="light.entity_id"
            class="flex items-center justify-between text-xs py-0.5">
            <span class="text-white/50 truncate flex-1">{{ light.attributes?.friendly_name || light.entity_id }}</span>
            <span :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
              {{ light.state === 'on' ? '● 开' : '○ 关' }}
            </span>
          </div>
        </div>
        <div class="text-xs text-white/30 mt-1">点击查看全部 →</div>
      </div>

      <!-- 空调 -->
      <div v-if="widgets.climate" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors"
        @click="$emit('open', 'climate')">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium">❄️ 空调</span>
          <span class="text-xs text-blue-300 font-bold">{{ summary.climate_total }} 台</span>
        </div>
        <div v-if="topClimates.length" class="space-y-1">
          <div v-for="c in topClimates" :key="c.entity_id"
            class="flex items-center justify-between text-xs py-0.5">
            <span class="text-white/50 truncate flex-1">{{ c.attributes?.friendly_name || c.entity_id }}</span>
            <span class="text-blue-300">{{ c.attributes?.temperature || '--' }}°</span>
          </div>
        </div>
        <div class="text-xs text-white/30 mt-1">点击查看全部 →</div>
      </div>

      <!-- 低电量 -->
      <div v-if="widgets.battery && lowBatteryEntities.length" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors border border-red-500/20"
        @click="$emit('open', 'battery')">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">🔋 低电量设备</span>
          <span class="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-bold">{{ lowBatteryEntities.length }} 个</span>
        </div>
      </div>

      <!-- 离线设备 -->
      <div v-if="widgets.offline && offlineEntities.length" class="glass-effect rounded-xl p-3 cursor-pointer card-hover transition-colors border border-orange-500/20"
        @click="$emit('open', 'offline')">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">📡 离线设备</span>
          <span class="text-xs px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 font-bold">{{ offlineEntities.length }} 个</span>
        </div>
      </div>

      <!-- 音乐 -->
      <div v-if="widgets.music" class="glass-effect rounded-xl cursor-pointer card-hover transition-colors"
        @click="$emit('open', 'music')">
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

defineEmits(['open'])

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
const weatherHumidity = computed(() => {
  const v = weatherEntity.value?.attributes?.humidity
  return v !== undefined && v !== null ? `${Math.round(Number(v))}%` : '--'
})
const weatherPrecipitation = computed(() => {
  const v = weatherEntity.value?.attributes?.precipitation
  return v !== undefined && v !== null ? `${Number(v).toFixed(1)}mm` : '0mm'
})
const weatherWind = computed(() => {
  const v = weatherEntity.value?.attributes?.wind_speed
  return v !== undefined && v !== null ? `${v}m/s` : null
})
const weatherEmoji = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  if (s.includes('fog') || s.includes('mist')) return '🌫️'
  if (s.includes('thunder')) return '⛈️'
  return '🌤️'
})

const topLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')).slice(0, 4))
const topClimates = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('climate.')).slice(0, 3))
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
