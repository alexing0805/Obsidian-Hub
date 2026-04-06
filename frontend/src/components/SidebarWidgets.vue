<template>
  <div class="flex flex-col h-full overflow-hidden p-6 space-y-6">
  
    <!-- 1. 独立时钟卡片 (极简高级) -->
    <div class="glass-panel rounded-[2rem] p-6 relative overflow-hidden shrink-0 shadow-2xl border border-white/10 ring-1 ring-white/10 bg-gradient-to-br from-white/10 to-transparent">
      <div class="flex flex-col items-center">
        <div class="text-6xl font-black tracking-tighter font-heading tabular-nums leading-none mb-3 text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">{{ currentTime }}</div>
        <div class="text-[11px] font-black uppercase tracking-[0.4em] text-white/30">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 2. 独立气象卡片 (和风天气适配) -->
    <div v-if="widgets.weather" class="glass-panel rounded-[2.5rem] p-6 relative overflow-hidden group shrink-0 border border-white/5 ring-1 ring-white/10 shadow-xl">
      <!-- 动态氛围背景 -->
      <div v-if="maConnected && playState === 'playing'" class="absolute inset-0 bg-cyan-500/5 blur-3xl -z-10 animate-pulse"></div>
      
      <div class="flex items-center justify-between mb-6 px-1">
        <div class="flex items-center gap-5">
          <span class="text-6xl drop-shadow-2xl filter brightness-110 group-hover:scale-110 transition-transform duration-500">{{ weatherEmoji }}</span>
          <div class="flex flex-col">
            <span class="text-4xl font-heading font-black leading-none text-white tracking-tighter">{{ weatherTemperature }}</span>
            <span class="text-[11px] font-black text-cyan-400/70 uppercase tracking-[0.2em] mt-2">{{ weatherText }}</span>
          </div>
        </div>
        
        <div class="flex flex-col items-end gap-2">
          <div class="px-4 py-1.5 rounded-2xl bg-white/5 border border-white/10 flex gap-3 text-[11px] font-black tabular-nums shadow-inner">
             <span class="text-red-400 flex items-center gap-1"><span class="text-[8px] opacity-40">H</span>{{ weatherHigh }}°</span>
             <span class="text-blue-400 flex items-center gap-1"><span class="text-[8px] opacity-40">L</span>{{ weatherLow }}°</span>
          </div>
          <div v-if="weatherHumidity !== '--'" class="text-[10px] font-black text-white/20 uppercase tracking-widest flex items-center gap-1.5">
             <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21c-4.418 0-8-3.582-8-8 0-4.418 8-11 8-11s8 6.582 8 11c0 4.418-3.582 8-8 8z"/></svg>
             {{ weatherHumidity }}
          </div>
        </div>
      </div>

      <!-- 未来三日迷你预报 -->
      <div v-if="weatherForecast.length" class="grid grid-cols-3 gap-3 pt-6 border-t border-white/10">
        <div v-for="(fc, idx) in weatherForecast" :key="idx" class="flex flex-col items-center py-3 rounded-2xl bg-white/[0.02] border border-transparent hover:border-white/10 hover:bg-white/5 transition-all duration-300">
          <span class="text-[10px] font-black text-white/20 uppercase mb-3 tracking-wider">{{ fc.weekday }}</span>
          <span class="text-3xl mb-2 filter drop-shadow-md">{{ getFcEmoji(fc.condition) }}</span>
          <span class="text-[12px] font-extrabold text-white/50">{{ fc.temp }}°</span>
        </div>
      </div>
      <div v-else class="text-center py-4 text-[10px] text-white/10 uppercase font-black italic tracking-[0.2em]">Syncing Forecast...</div>
    </div>
  
    <!-- 3. 自适应功能按键 (拉伸填满) -->
    <div class="flex flex-row gap-3 shrink-0">
      <template v-for="btn in activeStatusButtons" :key="btn.id">
        <div 
          class="glass-panel flex-1 flex flex-col items-center justify-center py-5 rounded-[2.5rem] card-hover cursor-pointer border-white/5 ring-1 ring-white/5 relative group transition-all min-w-0 shadow-lg"
          @click="$emit('open', btn.id)"
        >
          <div class="text-3xl mb-2.5 group-hover:scale-110 transition-transform duration-500">{{ btn.icon }}</div>
          <div class="text-[15px] font-black leading-none mb-1 shadow-sm" :class="btn.valueClass">{{ btn.value }}</div>
          <div class="text-[9px] font-black uppercase tracking-[0.15em] text-white/20">{{ btn.label }}</div>
          
          <!-- 活跃指示器 -->
          <div v-if="btn.active" class="absolute top-3 right-5 w-2 h-2 rounded-full animate-pulse shadow-[0_0_10px_currentColor]" :class="btn.indicatorClass"></div>
        </div>
      </template>
    </div>
  
    <!-- 4. 音乐播放器 (垂直 100% 占满) -->
    <div v-if="widgets.music" class="flex-1 flex flex-col min-h-0 min-w-0">
      <MusicAssistantPlayer :ma-state="maState" @select-player="$emit('select-player', $event)" />
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
 
const weatherEntity = computed(() => {
  // 1. 优先搜索和风天气
  const hefeng = props.haEntities.find(e => e.entity_id === 'weather.he_feng_tian_qi')
  if (hefeng) return hefeng
  
  // 2. 其次根据 ID 或带有预报的实体
  return props.haEntities.find(e => e.entity_id === props.weatherEntityId) ||
    props.haEntities.find(e => e.entity_id.startsWith('weather.') && (e.attributes?.forecast || e.attributes?.temp_high)) ||
    props.haEntities.find(e => e.entity_id.startsWith('weather.')) || null
})

// 从 summary 中优先读取后端聚合好的数据（因为后端现在会主动抓取服务预报）
const weatherData = computed(() => props.summary?.weather || {})

const weatherText = computed(() => weatherData.value?.state || weatherEntity.value?.state || '未知')
const weatherTemperature = computed(() => {
  const v = weatherData.value?.temperature || weatherEntity.value?.attributes?.temperature
  return v !== undefined && v !== null ? `${Math.round(Number(v))}°` : '--'
})
const weatherHumidity = computed(() => {
  const v = weatherData.value?.humidity || weatherEntity.value?.attributes?.humidity
  return v !== undefined && v !== null ? `${Math.round(Number(v))}%` : '--'
})
const weatherHigh = computed(() => {
  return weatherData.value?.temperature_high || '--'
})
const weatherLow = computed(() => {
  return weatherData.value?.temperature_low || '--'
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
  // 优先使用后端聚合的预报
  const fc = weatherData.value?.forecast || weatherEntity.value?.attributes?.forecast || []
  return fc.slice(0, 3).map(item => {
    try {
      const dt = item.datetime ? new Date(item.datetime) : new Date();
      return {
        weekday: dt.toLocaleDateString('zh-CN', { weekday: 'short' }),
        condition: item.condition,
        temp: item.temperature
      }
    } catch(e) {
      return { weekday: '?', condition: '', temp: '--' }
    }
  })
})

const weatherEmoji = computed(() => getFcEmoji(weatherText.value))
 
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
