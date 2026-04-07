<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-8" @click.self="$emit('close')">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-md transition-all duration-500" @click="$emit('close')"></div>

    <div class="relative glass-panel rounded-[2.5rem] w-full flex flex-col overflow-hidden shadow-[0_30px_60px_-15px_rgba(0,0,0,0.5)] border-white/10 ring-1 ring-white/5 animate-fade-in"
      :class="type === 'weather' ? 'max-w-2xl max-h-[80vh]' : 'max-w-4xl max-h-[88vh]'">

      <!-- 标题栏 -->
      <div class="flex items-center justify-between px-8 py-5 border-b border-white/5 shrink-0 bg-white/5">
        <div class="flex items-center gap-4 text-2xl font-extrabold font-heading tracking-tight text-white/90">
          <span class="opacity-80">{{ titleIcon }}</span>
          <span>{{ titleText }}</span>
        </div>
        <button class="w-12 h-12 rounded-2xl flex items-center justify-center text-white/30 hover:text-white hover:bg-white/10 transition-all active:scale-90 bg-white/5 border border-white/5"
          @click="$emit('close')">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 overflow-y-auto p-6">

        <!-- 灯光详情 -->
        <div v-if="type === 'lights'">
          <div class="grid grid-cols-3 gap-4">
            <div v-for="light in displayLights" :key="light.entity_id"
              class="glass-effect rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer transition-all border"
              :class="light.state === 'on' ? 'border-yellow-500/40 bg-yellow-500/5' : 'border-white/10 hover:border-white/20'"
              @click="toggleLight(light)">
              <div class="text-4xl">{{ light.state === 'on' ? '💡' : '🔦' }}</div>
              <div class="text-sm text-center text-white/70 truncate w-full">
                {{ light.attributes?.friendly_name || light.entity_id }}
              </div>
              <div class="text-sm" :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
                {{ light.state === 'on' ? '● 已开启' : '○ 已关闭' }}
              </div>
            </div>
          </div>
          <div v-if="!displayLights.length" class="text-center text-white/30 py-16">未检测到灯光设备</div>
        </div>

        <!-- 空调详情 -->
        <div v-if="type === 'climate'">
          <div v-if="displayClimates.length" class="space-y-6 animate-fade-in py-2">
            <div v-for="climate in displayClimates" :key="climate.entity_id"
              class="glass-panel rounded-[2rem] p-6 border border-white/5 bg-gradient-to-br from-white/[0.03] to-transparent shadow-2xl relative overflow-hidden group mb-4">

              <div class="absolute -top-24 -right-24 w-72 h-72 bg-blue-500/10 blur-[100px] pointer-events-none group-hover:bg-blue-500/20 transition-all duration-1000"></div>

              <div class="flex items-center justify-between mb-8">
                <div>
                  <div class="text-xl font-black tracking-tight text-white/90">{{ climate.attributes?.friendly_name || '空调' }}</div>
                  <div class="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400/60 mt-1">{{ climate.state }}模式</div>
                </div>
                <div class="flex items-center gap-3 bg-white/5 p-3 rounded-xl border border-white/10 shadow-inner">
                  <div class="text-right">
                    <div class="text-[10px] font-black text-white/20 uppercase">室内温度</div>
                    <div class="text-lg font-black text-white">{{ climate.attributes?.current_temperature || '--' }}°</div>
                  </div>
                  <div class="w-px h-8 bg-white/10"></div>
                  <div class="text-2xl">🌡️</div>
                </div>
              </div>

              <div class="flex items-center justify-center gap-10 mb-6">
                <button @click="setTemp(climate, (climate.attributes?.temperature || 24) - 0.5)"
                  class="w-14 h-14 rounded-full flex items-center justify-center border border-white/10 bg-white/5 text-2xl font-black text-white/40 hover:text-white hover:border-white/30 hover:scale-110 active:scale-90 transition-all shadow-lg">
                  －
                </button>
                <div class="relative flex flex-col items-center">
                  <div class="text-6xl font-black tracking-tighter text-white tabular-nums drop-shadow-[0_0_30px_rgba(255,255,255,0.2)] leading-none">
                    {{ Math.round(climate.attributes?.temperature || 24) }}<span class="text-2xl align-top mt-4 ml-0.5">°</span>
                  </div>
                </div>
                <button @click="setTemp(climate, (climate.attributes?.temperature || 24) + 0.5)"
                  class="w-14 h-14 rounded-full flex items-center justify-center border border-white/10 bg-white/5 text-2xl font-black text-white/40 hover:text-white hover:border-white/30 hover:scale-110 active:scale-90 transition-all shadow-lg">
                  ＋
                </button>
              </div>

              <div class="grid grid-cols-2 gap-6 pt-2">
                <div class="space-y-3">
                  <div class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] ml-2">运行模式</div>
                  <div class="flex flex-wrap gap-2">
                    <button v-for="mode in getHvacModes(climate)" :key="mode.value"
                      class="flex-1 min-w-[70px] px-3 py-2.5 text-[10px] font-black rounded-xl border transition-all uppercase tracking-wider"
                      :class="climate.state === mode.value ? 'border-blue-500/50 bg-blue-500/20 text-blue-400' : 'border-white/5 bg-white/[0.02] text-white/30'"
                      @click="setMode(climate, mode.value)">
                      <div class="text-lg mb-0.5">{{ mode.icon }}</div>
                      {{ mode.label }}
                    </button>
                  </div>
                </div>
                <div class="space-y-3">
                  <div class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] ml-2">风速</div>
                  <div class="flex flex-wrap gap-2">
                    <button v-for="fan in getFanModes(climate)" :key="fan"
                      class="flex-1 min-w-[60px] px-3 py-2.5 text-[10px] font-black rounded-xl border transition-all uppercase tracking-tighter"
                      :class="climate.attributes?.fan_mode === fan ? 'border-cyan-500/50 bg-cyan-500/20 text-cyan-400' : 'border-white/5 bg-white/[0.02] text-white/30'"
                      @click="setFanMode(climate, fan)">
                      <div class="text-lg mb-0.5">🌬️</div>
                      {{ fan }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center text-white/30 py-20 italic font-black uppercase tracking-widest bg-white/5 rounded-[3rem] border border-white/5">
             Searching Climate Entity...
          </div>
        </div>

        <!-- 窗帘详情 -->
        <div v-if="type === 'cover'" class="max-w-xl mx-auto">
          <div v-if="coverEntity" class="space-y-8 animate-fade-in">
            <div class="text-center">
              <div class="w-20 h-20 bg-blue-500/20 rounded-[2rem] flex items-center justify-center mx-auto mb-4 border border-blue-500/30">
                <IconCover class="w-10 h-10 text-blue-400" />
              </div>
              <h2 class="text-2xl font-black text-white tracking-tight leading-none">{{ coverEntity.attributes?.friendly_name }}</h2>
              <p class="text-[10px] font-black text-blue-400/60 uppercase tracking-[0.4em] mt-2">{{ coverEntity.state === 'open' ? '已开启' : '已关闭' }}</p>
            </div>

            <div class="grid grid-cols-3 gap-6">
              <button @click="onCoverAction('open_cover')" 
                class="flex flex-col items-center gap-3 p-6 rounded-[2rem] glass-panel border border-white/5 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all group active:scale-95">
                <div class="w-12 h-12 flex items-center justify-center bg-white/5 rounded-full group-hover:text-blue-400 transition-colors">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7"/></svg>
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest text-white/40 group-hover:text-white">开启</span>
              </button>
              
              <button @click="onCoverAction('stop_cover')" 
                class="flex flex-col items-center gap-3 p-6 rounded-[2rem] glass-panel border border-white/5 hover:border-white/40 hover:bg-white/15 transition-all group active:scale-95">
                <div class="w-12 h-12 flex items-center justify-center bg-white/5 rounded-full group-hover:text-white transition-colors">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest text-white/40 group-hover:text-white">停止</span>
              </button>

              <button @click="onCoverAction('close_cover')" 
                class="flex flex-col items-center gap-3 p-6 rounded-[2rem] glass-panel border border-white/5 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all group active:scale-95">
                <div class="w-12 h-12 flex items-center justify-center bg-white/5 rounded-full group-hover:text-blue-400 transition-colors">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg>
                </div>
                <span class="text-[10px] font-black uppercase tracking-widest text-white/40 group-hover:text-white">关闭</span>
              </button>
            </div>

            <div class="glass-panel p-6 rounded-[2rem] border border-white/5 bg-white/5">
              <div class="flex justify-between items-center mb-4">
                <span class="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">当前位置</span>
                <span class="text-2xl font-black text-blue-400 tabular-nums">{{ coverPosition }}%</span>
              </div>
              <input type="range" min="0" max="100" v-model="coverPosition" 
                class="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer accent-blue-500 hover:h-2 transition-all"
                @change="onCoverPositionChange" />
            </div>
          </div>
        </div>

        <!-- 天气详情 (和风天气重构) -->
        <div v-if="type === 'weather'">
          <div v-if="weatherEntity" class="animate-fade-in relative z-10 space-y-4">
            <div class="flex items-center justify-between bg-white/5 rounded-[2rem] p-6 border border-white/10 shadow-inner">
              <div class="flex items-center gap-6">
                <div class="text-7xl animate-bounce-subtle">{{ weatherEmoji }}</div>
                <div class="flex flex-col">
                  <div class="text-3xl font-black text-white leading-tight">{{ weatherText }}</div>
                  <div class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mt-1">和风天气 • 刚刚更新</div>
                </div>
              </div>
              <div class="flex flex-col items-end">
                <div class="text-5xl font-black text-white tracking-tighter leading-none mb-1">{{ weatherTemperature }}</div>
                <div class="flex gap-1 text-sm font-black tabular-nums">
                  <span class="text-blue-400">{{ weatherLow }}°</span>
                  <span class="text-white/40">/</span>
                  <span class="text-red-400">{{ weatherHigh }}°</span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-4 gap-3">
              <div v-for="attr in weatherAttrs" :key="attr.key" 
                class="glass-panel p-3.5 rounded-2xl flex flex-col items-center justify-center border border-white/5 bg-white/5">
                <div class="text-xl mb-1 opacity-80">{{ attr.icon }}</div>
                <div class="text-[9px] font-black text-white/20 uppercase tracking-widest mb-0.5">{{ attr.label }}</div>
                <div class="text-sm font-black text-white">{{ attr.value }}</div>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center gap-1 p-1 bg-black/20 rounded-xl w-fit mx-auto border border-white/5">
                <button v-for="mode in ['daily', 'hourly']" :key="mode"
                  @click="forecastMode = mode"
                  class="px-5 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all"
                  :class="forecastMode === mode ? 'bg-white/10 text-cyan-400 shadow-lg' : 'text-white/40 hover:text-white/60'">
                  {{ mode === 'daily' ? '每日' : '每小时' }}
                </button>
              </div>

              <div v-if="forecastMode === 'daily'" class="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hidden">
                <div v-for="(fc, idx) in forecastList" :key="idx" 
                  class="flex-shrink-0 w-24 glass-panel p-4 rounded-[1.5rem] flex flex-col items-center border border-white/5 bg-gradient-to-b from-white/5 to-transparent">
                  <span class="text-[10px] font-black text-white/30 uppercase mb-2 tracking-wider">{{ fc.weekday }}</span>
                  <span class="text-3xl mb-3">{{ getFcEmoji(fc.condition) }}</span>
                  <div class="flex flex-col items-center gap-0.5">
                    <span class="text-sm font-black text-white">{{ Math.round(fc.temp) }}°</span>
                    <span class="text-[10px] font-bold text-white/20">{{ Math.round(fc.templow) }}°</span>
                  </div>
                </div>
              </div>

              <div v-else class="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hidden">
                <div v-for="(fc, idx) in hourlyForecast" :key="idx" 
                  class="flex-shrink-0 w-20 glass-panel p-4 rounded-[1.5rem] flex flex-col items-center border border-white/5 bg-gradient-to-b from-white/5 to-transparent">
                  <span class="text-[10px] font-black text-white/30 uppercase mb-2 tracking-wider">{{ fc.hour }}</span>
                  <span class="text-2xl mb-2">{{ getFcEmoji(fc.condition) }}</span>
                  <span class="text-sm font-black text-white">{{ Math.round(fc.temp) }}°</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 电池详情 -->
        <div v-if="type === 'battery'">
          <div class="grid grid-cols-3 gap-4">
            <div v-for="battery in lowBatteryEntities" :key="battery.entity_id"
              class="glass-effect rounded-2xl p-5 flex flex-col items-center gap-3 border"
              :class="parseFloat(battery.state) <= 10 ? 'border-red-500/40 bg-red-500/5' : 'border-yellow-500/40 bg-yellow-500/5'">
              <div class="text-4xl">{{ parseFloat(battery.state) <= 10 ? '🔴' : '🟡' }}</div>
              <div class="text-sm text-center text-white/70 truncate w-full">{{ battery.attributes?.friendly_name || battery.entity_id }}</div>
              <div class="text-xl font-black text-white">{{ battery.state }}%</div>
            </div>
          </div>
          <div v-if="!lowBatteryEntities.length" class="text-center text-white/30 py-16">所有设备电量正常</div>
        </div>

        <!-- 离线详情 -->
        <div v-if="type === 'offline'">
          <div class="grid grid-cols-2 gap-4">
            <div v-for="entity in offlineEntities" :key="entity.entity_id"
              class="glass-effect rounded-2xl p-5 flex items-center gap-4 border border-orange-500/20 bg-orange-500/5">
              <div class="text-3xl">📡</div>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white/70 truncate">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
                <div class="text-xs text-orange-400/60 uppercase">{{ entity.state }}</div>
              </div>
            </div>
          </div>
          <div v-if="!offlineEntities.length" class="text-center text-white/30 py-16">所有设备在线</div>
        </div>

        <!-- 音乐详情 -->
        <div v-if="type === 'music'">
          <MusicAssistantPlayer :ma-state="maState" />
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, h } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'

const props = defineProps({
  type: { type: String, default: '' },
  entityId: { type: String, default: null },
  haEntities: { type: Array, default: () => [] },
  maState: { type: Object, default: () => ({}) },
  weatherEntityId: { type: String, default: '' },
  weatherForecast: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close', 'toggle-light', 'climate-action', 'cover-action'])

const IconCover = () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('rect', { width: '18', height: '18', x: '3', y: '3', rx: '2' }),
  h('path', { d: 'M9 3v18' }),
  h('path', { d: 'M15 3v18' })
])

const titleMap = {
  lights: { icon: '💡', text: 'LIGHTING' },
  climate: { icon: '❄️', text: 'CLIMATE' },
  weather: { icon: '🌤️', text: 'WEATHER' },
  battery: { icon: '🔋', text: 'BATTERY' },
  offline: { icon: '📡', text: 'OFFLINE' },
  music: { icon: '🎵', text: 'MUSIC' },
  cover: { icon: '🪟', text: 'CURTAINS' },
}
const titleIcon = computed(() => titleMap[props.type]?.icon || '')
const titleText = computed(() => titleMap[props.type]?.text || '')

const displayLights = computed(() => {
  const all = props.haEntities.filter(e => e.entity_id.startsWith('light.'))
  if (props.entityId) return all.filter(e => e.entity_id === props.entityId)
  return all
})

const displayClimates = computed(() => {
  const all = props.haEntities.filter(e => e.entity_id.startsWith('climate.'))
  if (props.entityId) return all.filter(e => e.entity_id === props.entityId)
  return all
})

const coverEntity = computed(() => props.haEntities.find(e => e.entity_id === props.entityId))
const coverPosition = ref(0)
watch(() => coverEntity.value?.attributes?.current_position, (val) => {
  if (val !== undefined) coverPosition.value = val
}, { immediate: true })

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

const weatherEntity = computed(() =>
  props.haEntities.find(e => e.entity_id === props.weatherEntityId) ||
  props.haEntities.find(e => e.entity_id.startsWith('weather.')) || null
)
const weatherTemperature = computed(() => {
  const v = weatherEntity.value?.attributes?.temperature
  return v !== undefined && v !== null ? `${Math.round(Number(v))}°` : '--'
})
const weatherLow = computed(() => {
  const fc0 = props.summary?.weather?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const val = fc0?.templow ?? fc0?.temperature_low ?? 0
  return Math.round(val)
})
const weatherHigh = computed(() => {
  const fc0 = props.summary?.weather?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const val = fc0?.temperature ?? fc0?.temp_high ?? 0
  return Math.round(val)
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

const weatherText = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  const map = {
    'sunny': '晴朗',
    'clear-night': '晴朗',
    'cloudy': '多云',
    'partlycloudy': '阴',
    'rainy': '雨',
    'snowy': '雪',
    'fog': '雾',
    'windy': '大风'
  }
  return map[s] || s.toUpperCase()
})

const forecastMode = ref('daily')
const weatherAttrs = computed(() => {
  if (!weatherEntity.value) return []
  const attrs = weatherEntity.value.attributes || {}
  return [
    { key: 'pressure', label: '气压', value: `${attrs.pressure || '--'} hPa`, icon: '⏲️' },
    { key: 'humidity', label: '湿度', value: `${attrs.humidity || '--'}%`, icon: '💧' },
    { key: 'wind_speed', label: '风速', value: `${attrs.wind_speed || '--'} km/h`, icon: '🌬️' },
    { key: 'visibility', label: '能见度', value: `${attrs.visibility || '--'} km`, icon: '👁️' },
  ]
})

const forecastList = computed(() => {
  const fc = props.summary?.weather?.forecast || weatherEntity.value?.attributes?.forecast || []
  return fc.map(item => {
    const tempHigh = item.temperature ?? item.temp_high ?? item.max_temp ?? 0
    const tempLow = item.templow ?? item.temperature_low ?? item.min_temp ?? 0
    return {
      weekday: item.datetime ? new Date(item.datetime).toLocaleDateString('zh-CN', { weekday: 'short' }) : '?',
      condition: item.condition,
      temp: Math.round(tempHigh),
      templow: Math.round(tempLow)
    }
  })
})

const hourlyForecast = computed(() => {
  const fc = props.summary?.weather?.hourly_forecast || []
  return fc.slice(0, 24).map(item => ({
    hour: item.datetime ? new Date(item.datetime).getHours() + '时' : '?',
    condition: item.condition,
    temp: Math.round(item.temperature ?? item.temp ?? 0)
  }))
})

const getFcEmoji = (cond) => {
  const s = (cond || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  return '🌤️'
}

const getHvacModes = (climate) => {
  const modes = climate.attributes?.hvac_modes || ['off', 'heat', 'cool', 'auto', 'dry', 'fan_only']
  const map = {
    'off': { label: '关', icon: '⭕' },
    'heat': { label: '制热', icon: '🔥' },
    'cool': { label: '制冷', icon: '❄️' },
    'auto': { label: '自动', icon: '🔄' },
    'dry': { label: '除湿', icon: '💧' },
    'fan_only': { label: '送风', icon: '🌬️' }
  }
  return modes.map(m => map[m] ? { ...map[m], value: m } : { value: m, label: m.toUpperCase(), icon: '⚙️' })
}

const getFanModes = (climate) => {
  return climate.attributes?.fan_mode_list || climate.attributes?.fan_modes || ['low', 'medium', 'high', 'auto']
}

const toggleLight = (entity) => emit('toggle-light', entity)
const setTemp = (entity, temp) => emit('climate-action', { entity, action: 'temp', value: temp })
const setMode = (entity, mode) => emit('climate-action', { entity, action: 'mode', value: mode })
const setFanMode = (entity, fan) => emit('climate-action', { entity, action: 'fan', value: fan })
const onCoverAction = (service) => {
  if (!coverEntity.value) return
  emit('cover-action', { service, entityId: coverEntity.value.entity_id })
}
const onCoverPositionChange = () => {
  if (!coverEntity.value) return
  emit('cover-action', { service: 'set_cover_position', entityId: coverEntity.value.entity_id, data: { position: parseInt(coverPosition.value) } })
}

</script>

<style scoped>
.animate-fade-in { animation: fade-in 0.4s ease-out; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.scrollbar-hidden::-webkit-scrollbar { display: none; }
@keyframes bounce-subtle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.animate-bounce-subtle { animation: bounce-subtle 3s ease-in-out infinite; }
</style>
