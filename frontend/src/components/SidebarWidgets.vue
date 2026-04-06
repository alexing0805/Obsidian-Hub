<template>
  <div class="flex flex-col h-full overflow-hidden p-4 space-y-4">
 
    <!-- 1. 灵动状态头 (时间 + 天气) -->
    <div class="glass-panel rounded-[2rem] p-6 relative overflow-hidden group shrink-0">
      <div v-if="maConnected && playState === 'playing'" class="absolute inset-0 bg-cyan-500/10 blur-3xl -z-10 animate-pulse"></div>
      
      <div class="flex items-center justify-between">
        <div class="flex flex-col">
          <div class="text-4xl font-extrabold tracking-tighter font-heading tabular-nums leading-none mb-2">{{ currentTime }}</div>
          <div class="text-[9px] font-black uppercase tracking-[0.2em] text-white/30">{{ currentDate }}</div>
        </div>
        <div class="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/5 cursor-pointer hover:bg-white/10 transition-all" @click="$emit('open', 'weather')">
           <span class="text-3xl filter drop-shadow-lg">{{ weatherEmoji }}</span>
           <div class="flex flex-col items-end">
             <span class="text-xl font-heading font-bold leading-none">{{ weatherTemperature }}</span>
             <span class="text-[9px] font-black text-cyan-400/60 uppercase tracking-tighter">{{ weatherText }}</span>
           </div>
        </div>
      </div>
    </div>
 
    <!-- 2. 功能矩阵 (1列 4个方形按钮) -->
    <div v-if="widgets.stats" class="flex flex-col gap-3 shrink-0">
      <!-- 灯光统计 -->
      <div class="glass-panel aspect-video md:aspect-square flex flex-col items-center justify-center p-3 rounded-[1.5rem] card-hover cursor-pointer border-white/5 relative group"
        @click="$emit('open', 'lights')">
        <div class="text-3xl mb-1 group-hover:scale-110 transition-transform">💡</div>
        <div class="text-lg font-heading font-black text-yellow-400 leading-none">{{ summary.lights_on }}<span class="text-[10px] text-white/20 font-medium ml-1">/{{ summary.lights_total }}</span></div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Lighting</div>
        <div v-if="summary.lights_on > 0" class="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-yellow-400 shadow-[0_0_8px_#fbbf24]"></div>
      </div>

      <!-- 空调统计 -->
      <div class="glass-panel aspect-video md:aspect-square flex flex-col items-center justify-center p-3 rounded-[1.5rem] card-hover cursor-pointer border-white/5 relative group"
        @click="$emit('open', 'climate')">
        <div class="text-3xl mb-1 group-hover:scale-110 transition-transform">❄️</div>
        <div class="text-lg font-heading font-black text-blue-400 leading-none">{{ summary.climate_online }}<span class="text-[10px] text-white/20 font-medium ml-1">/{{ summary.climate_total }}</span></div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Climate</div>
      </div>

      <!-- 电池状态 -->
      <div class="glass-panel aspect-video md:aspect-square flex flex-col items-center justify-center p-3 rounded-[1.5rem] card-hover cursor-pointer border-white/5 relative group"
        @click="$emit('open', 'battery')">
        <div class="text-3xl mb-1 group-hover:scale-110 transition-transform">🔋</div>
        <div class="text-lg font-heading font-black leading-none" :class="lowBatteryEntities.length ? 'text-red-400' : 'text-emerald-400'">
          {{ lowBatteryEntities.length || 'Full' }}
        </div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Battery</div>
        <div v-if="lowBatteryEntities.length" class="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-red-400 animate-ping"></div>
      </div>

      <!-- 离线状态 -->
      <div class="glass-panel aspect-video md:aspect-square flex flex-col items-center justify-center p-3 rounded-[1.5rem] card-hover cursor-pointer border-white/5 relative group"
        @click="$emit('open', 'offline')">
        <div class="text-3xl mb-1 group-hover:scale-110 transition-transform">📡</div>
        <div class="text-lg font-heading font-black leading-none" :class="offlineEntities.length ? 'text-orange-400' : 'text-white/20'">
          {{ offlineEntities.length || 'Online' }}
        </div>
        <div class="text-[9px] font-black uppercase tracking-widest text-white/30 mt-1">Status</div>
      </div>
    </div>
 
    <!-- 3. 音乐播放器 (占据剩余空间) -->
    <div v-if="widgets.music" class="flex-1 flex flex-col min-h-0 min-w-0">
      <div class="flex items-center justify-between px-2 mb-2 shrink-0">
        <span class="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">Music Player</span>
        <MusicPlayerSelector :ma-state="maState" class="text-[10px]" @select-player="$emit('select-player', $event)" />
      </div>
      <div class="flex-1 min-h-0 bg-white/5 rounded-[2rem] border border-white/5 overflow-hidden flex flex-col">
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
