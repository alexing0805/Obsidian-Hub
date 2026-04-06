<template>
  <div class="flex flex-col h-full overflow-hidden p-4 space-y-4">
  
    <!-- 1. 灵动状态头 (时间 + 详情天气) -->
    <div class="glass-panel rounded-[2rem] p-5 relative overflow-hidden group shrink-0">
      <!-- 动态氛围背景 -->
      <div v-if="maConnected && playState === 'playing'" class="absolute inset-0 bg-cyan-500/10 blur-3xl -z-10 animate-pulse"></div>
      
      <div class="flex items-center justify-between mb-4">
        <div class="flex flex-col">
          <div class="text-4xl font-extrabold tracking-tighter font-heading tabular-nums leading-none mb-1 text-white shadow-sm">{{ currentTime }}</div>
          <div class="text-[9px] font-black uppercase tracking-[0.2em] text-white/30">{{ currentDate }}</div>
        </div>
        
        <div class="flex flex-col items-end">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-3xl drop-shadow-md">{{ weatherEmoji }}</span>
            <div class="flex flex-col items-end">
              <span class="text-xl font-heading font-bold leading-none text-white">{{ weatherTemperature }}</span>
              <div class="flex gap-1.5 text-[8px] font-black uppercase tracking-tighter text-cyan-400/60 mt-0.5">
                 <span>H:{{ weatherHigh }}°</span>
                 <span>L:{{ weatherLow }}°</span>
              </div>
            </div>
          </div>
          <span class="text-[8px] font-black text-white/20 uppercase tracking-[0.1em]">{{ weatherText }}</span>
        </div>
      </div>

      <!-- 未来三日预报 -->
      <div v-if="weatherForecast.length" class="flex justify-between items-center pt-3 border-t border-white/5 mx-1">
        <div v-for="(fc, idx) in weatherForecast" :key="idx" class="flex flex-col items-center flex-1">
          <span class="text-[8px] font-black text-white/20 uppercase mb-1">{{ fc.weekday }}</span>
          <span class="text-lg mb-0.5">{{ getFcEmoji(fc.condition) }}</span>
          <span class="text-[9px] font-bold text-white/40">{{ fc.temp }}°</span>
        </div>
      </div>
    </div>
  
    <!-- 2. 功能矩阵 (1x4 或 2x4 横向平铺) -->
    <div class="grid grid-cols-4 gap-2 shrink-0">
      <template v-for="btn in activeStatusButtons" :key="btn.id">
        <div 
          class="glass-panel flex flex-col items-center justify-center py-2.5 rounded-2xl card-hover cursor-pointer border-white/5 relative group transition-all"
          @click="$emit('open', btn.id)"
        >
          <div class="text-xl mb-1 group-hover:scale-110 transition-transform">{{ btn.icon }}</div>
          <div class="text-[11px] font-black leading-none mb-0.5" :class="btn.valueClass">{{ btn.value }}</div>
          <div class="text-[7px] font-black uppercase tracking-wider text-white/20">{{ btn.label }}</div>
          
          <!-- 活跃指示器 -->
          <div v-if="btn.active" class="absolute top-1.5 right-1.5 w-1 h-1 rounded-full animate-pulse" :class="btn.indicatorClass"></div>
        </div>
      </template>
    </div>
  
    <!-- 3. 极速音乐播放器 (占据剩余空间) -->
    <div v-if="widgets.music" class="flex-1 flex flex-col min-h-0 min-w-0">
      <div class="flex-1 min-h-0">
        <MusicAssistantPlayer :ma-state="maState" @select-player="$emit('select-player', $event)" />
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
  return v !== undefined && v !== null ? `${Math.round(Number(v))}°` : '--'
})
const weatherHigh = computed(() => {
  const a = weatherEntity.value?.attributes || {}
  return a.temperature_high || (a.forecast?.[0]?.temperature) || '--'
})
const weatherLow = computed(() => {
  const a = weatherEntity.value?.attributes || {}
  return a.temperature_low || (a.forecast?.[0]?.templow) || '--'
})

const getFcEmoji = (cond) => {
  const s = (cond || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  if (s.includes('fog') || s.includes('mist')) return '🌫️'
  return '🌤️'
}

const weatherForecast = computed(() => {
  const fc = weatherEntity.value?.attributes?.forecast || []
  return fc.slice(1, 4).map(item => {
    try {
      return {
        weekday: new Date(item.datetime).toLocaleDateString('zh-CN', { weekday: 'short' }),
        condition: item.condition,
        temp: item.temperature
      }
    } catch(e) {
      return { weekday: '?', condition: '', temp: '--' }
    }
  })
})

const weatherEmoji = computed(() => getFcEmoji(weatherEntity.value?.state))
 
const activeStatusButtons = computed(() => {
  const btns = []
  
  if (widgets.value.lights) {
    btns.push({
      id: 'lights',
      label: 'Lighting',
      icon: '💡',
      value: `${props.summary.lights_on || 0}/${props.summary.lights_total || 0}`,
      valueClass: 'text-yellow-400',
      active: (props.summary.lights_on || 0) > 0,
      indicatorClass: 'bg-yellow-400 shadow-[0_0_8px_#fbbf24]'
    })
  }
  
  if (widgets.value.climate) {
    btns.push({
      id: 'climate',
      label: 'Climate',
      icon: '❄️',
      value: props.summary.climate_online || 0,
      valueClass: 'text-blue-400',
      active: (props.summary.climate_online || 0) > 0,
      indicatorClass: 'bg-blue-400'
    })
  }
  
  if (widgets.value.battery) {
    const lowCount = lowBatteryEntities.value.length
    btns.push({
      id: 'battery',
      label: 'Battery',
      icon: '🔋',
      value: lowCount > 0 ? lowCount : 'Full',
      valueClass: lowCount > 0 ? 'text-red-400' : 'text-emerald-400',
      active: lowCount > 0,
      indicatorClass: 'bg-red-400 shadow-[0_0_8px_#f87171]'
    })
  }
  
  if (widgets.value.offline) {
    const offlineCount = offlineEntities.value.length
    btns.push({
      id: 'offline',
      label: 'Status',
      icon: '📡',
      value: offlineCount > 0 ? offlineCount : 'Online',
      valueClass: offlineCount > 0 ? 'text-orange-400' : 'text-white/20',
      active: offlineCount > 0,
      indicatorClass: 'bg-orange-400'
    })
  }
  
  return btns
})

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
