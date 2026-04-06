<template>
  <div class="flex flex-col h-full overflow-hidden p-6 space-y-6">
  
    <!-- 1. 独立时钟卡片 (极简高级) -->
    <div class="glass-panel rounded-[2rem] p-5 relative overflow-hidden shrink-0 shadow-xl border border-white/10 ring-1 ring-white/10 bg-gradient-to-br from-white/10 to-transparent">
      <div class="flex flex-col items-center">
        <div class="text-5xl font-black tracking-tighter font-heading tabular-nums leading-none mb-2 text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">{{ currentTime }}</div>
        <div class="text-[10px] font-black uppercase tracking-[0.3em] text-white/30">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 2. 精简气象卡片 (基础信息) -->
    <div v-if="widgets.weather" class="glass-panel rounded-[2rem] p-5 relative overflow-hidden group shrink-0 border border-white/5 ring-1 ring-white/10 shadow-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-5xl drop-shadow-lg group-hover:scale-105 transition-transform duration-500">{{ weatherEmoji }}</span>
          <div class="flex flex-col">
            <span class="text-3xl font-heading font-black leading-none text-white tracking-tighter">{{ weatherTemperature }}</span>
            <span class="text-[10px] font-black text-cyan-400/60 uppercase tracking-widest mt-1">{{ weatherText }}</span>
          </div>
        </div>
        
        <div class="flex flex-col items-end gap-1">
          <div class="px-3 py-1 rounded-xl bg-white/5 border border-white/10 flex gap-2 text-[10px] font-black tabular-nums shadow-inner">
             <span class="text-red-400">H: {{ weatherHigh }}°</span>
             <span class="text-blue-400">L: {{ weatherLow }}°</span>
          </div>
          <div v-if="weatherHumidity !== '--'" class="text-[9px] font-black text-white/10 uppercase tracking-tighter">Humi: {{ weatherHumidity }}</div>
        </div>
      </div>
    </div>
  
    <!-- 3. 自适应功能按键 (拉伸填满) -->
    <div class="flex flex-row gap-3 shrink-0">
      <template v-for="btn in activeStatusButtons" :key="btn.id">
        <div 
          class="glass-panel flex-1 flex flex-col items-center justify-center py-4 rounded-[2rem] card-hover cursor-pointer border-white/5 ring-1 ring-white/5 relative group transition-all min-w-0 shadow-md"
          @click="$emit('open', btn.id)"
        >
          <div class="text-2xl mb-1.5 group-hover:scale-110 transition-transform duration-500">{{ btn.icon }}</div>
          <div class="text-[12px] font-black leading-none mb-0.5" :class="btn.valueClass">{{ btn.value }}</div>
          <div class="text-[7px] font-black uppercase tracking-wider text-white/20">{{ btn.label }}</div>
          
          <!-- 活跃指示器 -->
          <div v-if="btn.active" class="absolute top-2 right-4 w-1.5 h-1.5 rounded-full animate-pulse shadow-sm" :class="btn.indicatorClass"></div>
        </div>
      </template>
    </div>
  
    <!-- 4. 音乐播放器 (占据核心纵向空间) -->
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
