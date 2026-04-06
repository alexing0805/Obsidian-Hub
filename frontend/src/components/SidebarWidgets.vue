<template>
  <div class="flex flex-col h-full">

    <!-- 顶部时钟 -->
    <div class="p-8 border-b border-white/5 shrink-0 relative overflow-hidden group">
      <div v-if="maConnected && playState === 'playing'" class="absolute inset-0 bg-cyan-500/5 blur-3xl -z-10 animate-pulse"></div>
      <div class="text-center">
        <div class="text-5xl font-extrabold tracking-tight font-heading tabular-nums">{{ currentTime }}</div>
        <div class="text-[10px] font-black uppercase tracking-[0.3em] text-white/30 mt-2">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 天气 (大卡片) -->
    <div v-if="widgets.weather && weatherEntity" class="px-6 py-4 shrink-0">
      <div class="glass-panel rounded-3xl p-5 card-hover relative overflow-hidden cursor-pointer"
        @click="$emit('open', 'weather')">
        <div class="flex items-center justify-between mb-4">
          <div class="flex flex-col">
            <span class="text-[10px] font-black uppercase tracking-widest text-cyan-400/60 mb-1">Current Weather</span>
            <span class="text-2xl font-heading font-bold">{{ weatherText }}</span>
          </div>
          <span class="text-5xl drop-shadow-2xl">{{ weatherEmoji }}</span>
        </div>
        
        <div class="flex items-end gap-3">
          <span class="text-4xl font-heading font-extrabold">{{ weatherTemperature }}</span>
          <div class="flex-1 border-b border-white/10 mb-2"></div>
          <div class="text-right flex flex-col gap-0.5">
            <div class="text-[10px] font-bold text-white/40 uppercase">Humidity <span class="text-white/80 ml-1 font-heading">{{ weatherHumidity }}</span></div>
            <div class="text-[10px] font-bold text-white/40 uppercase">Wind <span class="text-white/80 ml-1 font-heading">{{ weatherWind || '--' }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 侧边快捷统计 (网格化) -->
    <div v-if="widgets.stats" class="px-6 py-2 shrink-0 grid grid-cols-2 gap-3">
      <div class="glass-panel p-4 rounded-3xl card-hover cursor-pointer" @click="$emit('open', 'lights')">
        <div class="text-2xl mb-1">💡</div>
        <div class="text-lg font-heading font-extrabold text-yellow-400">{{ summary.lights_on }}<span class="text-xs text-white/20 font-medium ml-1">/ {{ summary.lights_total }}</span></div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Lights</div>
      </div>
      <div class="glass-panel p-4 rounded-3xl card-hover cursor-pointer" @click="$emit('open', 'climate')">
        <div class="text-2xl mb-1">❄️</div>
        <div class="text-lg font-heading font-extrabold text-blue-400">{{ summary.climate_online }}<span class="text-xs text-white/20 font-medium ml-1">/ {{ summary.climate_total }}</span></div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Climate</div>
      </div>
    </div>

    <!-- 列表（可滚动） -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4">

      <!-- 灯光详细 (精简) -->
      <div v-if="widgets.lights && topLights.length" class="space-y-3">
        <div class="flex items-center justify-between px-2">
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">Lighting Control</span>
          <button class="text-[9px] font-bold text-yellow-400/60 uppercase hover:text-yellow-400" @click="$emit('open', 'lights')">View All</button>
        </div>
        <div class="flex flex-wrap gap-2.5">
          <div v-for="light in topLights.slice(0, 10)" :key="light.entity_id"
            class="w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-300 transform active:scale-90"
            :class="light.state === 'on' ? 'bg-yellow-400 text-black shadow-[0_4px_12px_rgba(251,191,36,0.4)]' : 'glass-panel text-white/20 hover:bg-white/5'"
            @click.stop="$emit('toggle-light', { entity_id: light.entity_id, type: '灯' })"
            :title="light.attributes?.friendly_name || light.entity_id">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M14 12a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
          </div>
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

const maConnected = computed(() => props.maState?.connected || false)
const playState = computed(() => props.maState?.active_player?.state || 'off')

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
