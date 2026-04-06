<template>
  <div class="flex flex-col h-full">

    <!-- 顶部时钟 -->
    <div class="p-4 border-b border-white/10 shrink-0">
      <div class="text-center">
        <div class="text-3xl font-light tracking-wider">{{ currentTime }}</div>
        <div class="text-xs text-white/40 mt-0.5">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 天气（紧凑合并） -->
    <div v-if="widgets.weather && weatherEntity" class="px-4 py-2 border-b border-white/5 shrink-0">
      <div class="flex items-center gap-2 cursor-pointer rounded-lg px-2 py-1 hover:bg-white/5 transition-colors"
        @click="$emit('open', 'weather')">
        <span class="text-xl">{{ weatherEmoji }}</span>
        <div class="flex-1">
          <div class="text-sm font-medium">{{ weatherTemperature }}</div>
          <div class="text-xs text-white/40">{{ weatherText }}</div>
        </div>
        <div class="text-right text-xs text-white/30">
          <div>💧 {{ weatherHumidity }}</div>
          <div>🌬️ {{ weatherWind || '--' }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷统计行 -->
    <div v-if="widgets.stats" class="px-4 py-2 border-b border-white/5 shrink-0 flex gap-2">
      <div class="flex-1 rounded-lg px-2 py-1.5 text-center cursor-pointer hover:bg-white/5 transition-colors"
        @click="$emit('open', 'lights')">
        <div class="text-sm font-bold text-yellow-300">💡 {{ summary.lights_on }}/{{ summary.lights_total }}</div>
        <div class="text-xs text-white/30">灯光</div>
      </div>
      <div class="flex-1 rounded-lg px-2 py-1.5 text-center cursor-pointer hover:bg-white/5 transition-colors"
        @click="$emit('open', 'climate')">
        <div class="text-sm font-bold text-blue-300">❄️ {{ summary.climate_online }}/{{ summary.climate_total }}</div>
        <div class="text-xs text-white/30">空调</div>
      </div>
      <div class="flex-1 rounded-lg px-2 py-1.5 text-center cursor-pointer hover:bg-white/5 transition-colors"
        @click="$emit('open', 'battery')">
        <div class="text-sm font-bold" :class="summary.low_battery_count ? 'text-red-300' : 'text-white/30'">
          🔋 {{ summary.low_battery_count || 0 }}
        </div>
        <div class="text-xs text-white/30">低电量</div>
      </div>
      <div class="flex-1 rounded-lg px-2 py-1.5 text-center cursor-pointer hover:bg-white/5 transition-colors"
        @click="$emit('open', 'offline')">
        <div class="text-sm font-bold" :class="summary.offline_count ? 'text-orange-300' : 'text-white/30'">
          📡 {{ summary.offline_count || 0 }}
        </div>
        <div class="text-xs text-white/30">离线</div>
      </div>
    </div>

    <!-- 列表（可滚动） -->
    <div class="flex-1 overflow-y-auto p-3 space-y-1.5">

      <!-- 灯光详细 -->
      <div v-if="widgets.lights && topLights.length" class="rounded-xl p-3 border border-yellow-500/10">
        <div class="flex items-center justify-between mb-2 cursor-pointer" @click="$emit('open', 'lights')">
          <span class="text-xs text-white/40">💡 灯光</span>
          <span class="text-xs text-yellow-300">点击详情 →</span>
        </div>
        <div class="flex flex-wrap gap-1">
          <div v-for="light in topLights.slice(0, 8)" :key="light.entity_id"
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs cursor-pointer transition-all"
            :class="light.state === 'on' ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/30' : 'bg-white/5 text-white/30 border border-white/10'"
            @click.stop="$emit('toggle-light', { entity_id: light.entity_id, type: '灯' })"
            :title="light.attributes?.friendly_name || light.entity_id">
            💡
          </div>
          <div v-if="topLights.length > 8" class="text-xs text-white/30 flex items-center">+{{ topLights.length - 8 }}</div>
        </div>
      </div>

      <!-- 空调详细 -->
      <div v-if="widgets.climate && topClimates.length" class="rounded-xl p-3 border border-blue-500/10">
        <div class="flex items-center justify-between mb-2 cursor-pointer" @click="$emit('open', 'climate')">
          <span class="text-xs text-white/40">❄️ 空调</span>
          <span class="text-xs text-blue-300">点击详情 →</span>
        </div>
        <div class="space-y-1">
          <div v-for="c in topClimates.slice(0, 3)" :key="c.entity_id"
            class="flex items-center justify-between text-xs py-0.5 cursor-pointer hover:bg-white/5 rounded px-1"
            @click.stop="$emit('open', 'climate')">
            <span class="text-white/60 truncate">{{ c.attributes?.friendly_name || c.entity_id }}</span>
            <span class="text-blue-300 shrink-0 ml-1">{{ c.attributes?.temperature || '--' }}°</span>
          </div>
        </div>
      </div>

      <!-- 低电量警告 -->
      <div v-if="widgets.battery && lowBatteryEntities.length"
        class="rounded-xl p-3 border border-red-500/20 cursor-pointer hover:bg-red-500/5 transition-colors"
        @click="$emit('open', 'battery')">
        <div class="flex items-center justify-between">
          <span class="text-xs text-red-400 font-medium">🔋 低电量 ({{ lowBatteryEntities.length }})</span>
          <span class="text-xs text-red-400/50">详情 →</span>
        </div>
      </div>

      <!-- 离线警告 -->
      <div v-if="widgets.offline && offlineEntities.length"
        class="rounded-xl p-3 border border-orange-500/20 cursor-pointer hover:bg-orange-500/5 transition-colors"
        @click="$emit('open', 'offline')">
        <div class="flex items-center justify-between">
          <span class="text-xs text-orange-400 font-medium">📡 离线 ({{ offlineEntities.length }})</span>
          <span class="text-xs text-orange-400/50">详情 →</span>
        </div>
      </div>

      <!-- 音乐 -->
      <div v-if="widgets.music" class="rounded-xl p-3 border border-purple-500/10">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-white/40">🎵 音乐</span>
          <MusicPlayerSelector :ma-state="maState" class="text-xs" @select-player="$emit('select-player', $event)" />
        </div>
        <MusicAssistantPlayer :ma-state="maState" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'
import MusicPlayerSelector from './MusicPlayerSelector.vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  maState: { type: Object, default: () => ({}) },
  currentTime: { type: String, default: '' },
  currentDate: { type: String, default: '' },
  weatherEntityId: { type: String, default: '' },
  sidebarWidgets: { type: Object, default: () => ({}) },
})

defineEmits(['open', 'toggle-light', 'select-player'])

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
