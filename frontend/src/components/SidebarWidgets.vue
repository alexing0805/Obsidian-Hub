<template>
  <div class="flex flex-col h-full overflow-hidden p-6 space-y-6">
  
    <!-- 1. 独立时钟卡片 -->
    <div class="glass-panel rounded-[2rem] p-6 relative overflow-hidden shrink-0 shadow-lg border border-white/5">
      <div class="flex flex-col items-center">
        <div class="text-5xl font-black tracking-tighter font-heading tabular-nums leading-none mb-2 text-white drop-shadow-xl">{{ currentTime }}</div>
        <div class="text-[10px] font-black uppercase tracking-[0.3em] text-white/40">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 2. 独立气象卡片 -->
    <div v-if="widgets.weather" class="glass-panel rounded-[2.5rem] p-6 relative overflow-hidden group shrink-0 border border-white/5">
      <!-- 动态氛围背景 -->
      <div v-if="maConnected && playState === 'playing'" class="absolute inset-0 bg-cyan-500/5 blur-3xl -z-10 animate-pulse"></div>
      
      <div class="flex items-center justify-between mb-6 px-1">
        <div class="flex items-center gap-4">
          <span class="text-5xl drop-shadow-2xl filter brightness-110">{{ weatherEmoji }}</span>
          <div class="flex flex-col">
            <span class="text-3xl font-heading font-black leading-none text-white">{{ weatherTemperature }}</span>
            <span class="text-[10px] font-black text-cyan-400/80 uppercase tracking-widest mt-1">{{ weatherText }}</span>
          </div>
        </div>
        
        <div class="flex flex-col items-end gap-1">
          <div class="px-3 py-1 rounded-full bg-white/5 border border-white/10 flex gap-2 text-[10px] font-black tabular-nums">
             <span class="text-red-400">H: {{ weatherHigh }}°</span>
             <span class="text-blue-400">L: {{ weatherLow }}°</span>
          </div>
          <div v-if="weatherHumidity !== '--'" class="text-[9px] font-black text-white/20 uppercase">Humidity: {{ weatherHumidity }}</div>
        </div>
      </div>

      <!-- 未来三日迷你预报 -->
      <div v-if="weatherForecast.length" class="grid grid-cols-3 gap-2 pt-5 border-t border-white/5">
        <div v-for="(fc, idx) in weatherForecast" :key="idx" class="flex flex-col items-center py-2 rounded-2xl hover:bg-white/5 transition-colors">
          <span class="text-[9px] font-black text-white/30 uppercase mb-2">{{ fc.weekday }}</span>
          <span class="text-2xl mb-1 filter drop-shadow-sm">{{ getFcEmoji(fc.condition) }}</span>
          <span class="text-[11px] font-extrabold text-white/60">{{ fc.temp }}°</span>
        </div>
      </div>
      <div v-else class="text-center py-2 text-[10px] text-white/10 uppercase font-black italic tracking-widest">No Forecast Data</div>
    </div>
  
    <!-- 3. 自适应功能按键 (根据数量自动拉伸填满) -->
    <div class="flex flex-row gap-3 shrink-0">
      <template v-for="btn in activeStatusButtons" :key="btn.id">
        <div 
          class="glass-panel flex-1 flex flex-col items-center justify-center py-4 rounded-[2rem] card-hover cursor-pointer border-white/5 relative group transition-all min-w-0"
          @click="$emit('open', btn.id)"
        >
          <div class="text-2xl mb-2 group-hover:scale-110 transition-transform">{{ btn.icon }}</div>
          <div class="text-[14px] font-black leading-none mb-1 shadow-sm" :class="btn.valueClass">{{ btn.value }}</div>
          <div class="text-[8px] font-black uppercase tracking-[0.1em] text-white/30">{{ btn.label }}</div>
          
          <!-- 活跃指示器 -->
          <div v-if="btn.active" class="absolute top-2 right-4 w-1.5 h-1.5 rounded-full animate-pulse shadow-lg" :class="btn.indicatorClass"></div>
        </div>
      </template>
    </div>
  
    <!-- 4. 音乐播放器 (增加间距与呼吸感) -->
    <div v-if="widgets.music" class="flex-1 flex flex-col min-h-0 min-w-0 pt-2">
      <div class="flex-1 min-h-0 bg-white/5 rounded-[3rem] border border-white/5 overflow-hidden flex flex-col shadow-inner">
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
  props.haEntities.find(e => e.entity_id.startsWith('weather.') && e.attributes?.forecast) ||
  props.haEntities.find(e => e.entity_id.startsWith('weather.')) || null
)
const weatherText = computed(() => weatherEntity.value?.state || '未知')
const weatherTemperature = computed(() => {
  const v = weatherEntity.value?.attributes?.temperature
  return v !== undefined && v !== null ? `${Math.round(Number(v))}°` : '--'
})
const weatherHumidity = computed(() => {
  const v = weatherEntity.value?.attributes?.humidity
  return v !== undefined && v !== null ? `${Math.round(Number(v))}%` : '--'
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
      indicatorClass: 'bg-yellow-400'
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
      indicatorClass: 'bg-red-400'
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
