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
        <div v-if="type === 'cover'">
          <div v-if="displayCovers.length" class="space-y-6 animate-fade-in py-2">
            <div v-for="cover in displayCovers" :key="cover.entity_id"
              class="glass-panel rounded-[3rem] p-10 border border-white/5 bg-gradient-to-br from-white/[0.03] to-transparent shadow-2xl relative overflow-hidden">

              <div class="flex items-center justify-between mb-10">
                <div>
                  <div class="text-3xl font-black tracking-tight text-white/90">{{ cover.attributes?.friendly_name || '窗帘' }}</div>
                  <div class="text-sm font-bold uppercase tracking-[0.3em] text-cyan-400/60 mt-2">{{ cover.state }}</div>
                </div>
                <div class="text-5xl">🪟</div>
              </div>

              <div class="grid grid-cols-3 gap-6 mb-12">
                <button @click="$emit('cover-action', { entity: cover, action: 'open_cover' })"
                  class="aspect-square rounded-[2rem] flex flex-col items-center justify-center border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/30 transition-all group">
                  <div class="text-5xl mb-3 group-hover:scale-110 transition-transform">🔼</div>
                  <span class="text-xs font-black uppercase tracking-widest text-white/40">OPEN</span>
                </button>
                <button @click="$emit('cover-action', { entity: cover, action: 'stop_cover' })"
                  class="aspect-square rounded-[2rem] flex flex-col items-center justify-center border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/30 transition-all group">
                  <div class="text-5xl mb-3 group-hover:scale-110 transition-transform">⏹️</div>
                  <span class="text-xs font-black uppercase tracking-widest text-white/40">STOP</span>
                </button>
                <button @click="$emit('cover-action', { entity: cover, action: 'close_cover' })"
                  class="aspect-square rounded-[2rem] flex flex-col items-center justify-center border border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/30 transition-all group">
                  <div class="text-5xl mb-3 group-hover:scale-110 transition-transform">🔽</div>
                  <span class="text-xs font-black uppercase tracking-widest text-white/40">CLOSE</span>
                </button>
              </div>

              <div v-if="cover.attributes?.current_position !== undefined" class="space-y-4 px-4">
                <div class="flex justify-between items-end">
                  <div class="text-xs font-black text-white/20 uppercase tracking-[0.5em]">当前位置</div>
                  <div class="text-3xl font-black text-cyan-400 tabular-nums">{{ cover.attributes.current_position }}%</div>
                </div>
                <input type="range" min="0" max="100" step="1"
                  :value="cover.attributes.current_position"
                  class="w-full h-3 bg-white/10 rounded-full appearance-none cursor-pointer accent-cyan-400"
                  @change="$emit('cover-action', { entity: cover, action: 'set_cover_position', value: $event.target.value })" />
              </div>
            </div>
          </div>
        </div>

        <!-- 天气详情 -->
        <div v-if="type === 'weather'">
          <div v-if="weatherEntity" class="space-y-4 py-2 animate-fade-in relative z-10">
            <div class="text-center py-2">
              <div class="text-4xl mb-2 drop-shadow-2xl animate-bounce-subtle">{{ weatherEmoji }}</div>
              <div class="text-3xl font-black tracking-tighter text-white">{{ weatherTemperature }}</div>
              <div class="text-lg font-black text-cyan-400 mt-1 uppercase tracking-[0.4em]">{{ weatherText }}</div>
              <div class="text-[9px] font-bold text-white/20 mt-0.5 uppercase tracking-widest">{{ weatherEntity.attributes?.friendly_name }}</div>
            </div>
            <div class="grid grid-cols-4 gap-3 px-2">
              <div v-for="attr in weatherAttrs" :key="attr.key"
                class="glass-panel rounded-xl p-3 text-center border border-white/5 shadow-inner hover:border-white/20 hover:bg-white/5 transition-all">
                <div class="text-[9px] font-black text-white/20 uppercase mb-1 tracking-widest">{{ attr.label }}</div>
                <div class="text-base font-black text-white/90">{{ attr.value }}</div>
              </div>
            </div>
            <div v-if="sidebarForecast.length" class="space-y-2 px-1 pt-3 border-t border-white/5">
              <div class="text-[9px] font-black text-white/20 uppercase tracking-[0.4em] ml-2">7日天气预报</div>
              <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hidden">
                <div v-for="(fc, idx) in sidebarForecast" :key="idx"
                  class="flex-shrink-0 w-24 glass-panel p-3 rounded-xl flex flex-col items-center border border-white/5">
                  <span class="text-[9px] font-black text-white/30 uppercase mb-1.5">{{ fc.weekday }}</span>
                  <span class="text-2xl mb-1.5 filter drop-shadow-md">{{ getFcEmoji(fc.condition) }}</span>
                  <div class="flex flex-col items-center">
                    <span class="text-base font-black text-white">{{ fc.temp }}°</span>
                  </div>
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
              <div class="text-sm text-center text-white/70 truncate w-full">
                {{ battery.attributes?.friendly_name || battery.entity_id }}
              </div>
              <div class="text-xl font-black" :class="parseFloat(battery.state) <= 10 ? 'text-red-400' : 'text-yellow-400'">
                {{ battery.state }}%
              </div>
            </div>
          </div>
          <div v-if="!lowBatteryEntities.length" class="text-center text-white/30 py-16">所有设备电量正常</div>
        </div>

        <!-- 离线设备详情 -->
        <div v-if="type === 'offline'">
          <div class="grid grid-cols-2 gap-4">
            <div v-for="entity in offlineEntities" :key="entity.entity_id"
              class="glass-effect rounded-2xl p-5 flex items-center gap-4 border border-orange-500/20 bg-orange-500/5">
              <div class="text-3xl">📡</div>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white/70 truncate">
                  {{ entity.attributes?.friendly_name || entity.entity_id }}
                </div>
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
import { computed } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'

const props = defineProps({
  type: { type: String, default: '' },
  entityId: { type: String, default: null },
  haEntities: { type: Array, default: () => [] },
  maState: { type: Object, default: () => ({}) },
  weatherEntityId: { type: String, default: '' },
  weatherForecast: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'toggle-light', 'climate-action', 'cover-action'])

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

const displayCovers = computed(() => {
  const all = props.haEntities.filter(e => e.entity_id.startsWith('cover.'))
  if (props.entityId) return all.filter(e => e.entity_id === props.entityId)
  return all
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

const weatherEntity = computed(() =>
  props.haEntities.find(e => e.entity_id === props.weatherEntityId) ||
  props.haEntities.find(e => e.entity_id.startsWith('weather.')) || null
)
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
  if (s.includes('fog') || s.includes('mist')) return '🌫️'
  return '🌤️'
})
const weatherText = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  const map = {
    'sunny': '晴朗', 'clear-night': '晴朗夜间', 'cloudy': '多云', 'partlycloudy': '阴天',
    'rainy': '有雨', 'pouring': '大雨', 'snowy': '有雪', 'fog': '有雾', 'mist': '薄雾',
    'thunderstorm': '雷阵雨', 'windy': '刮风', 'hail': '冰雹'
  }
  return map[s] || s.toUpperCase()
})
const weatherAttrs = computed(() => {
  const a = weatherEntity.value?.attributes || {}
  const attrs = []
  if (a.humidity !== undefined) attrs.push({ key: 'hum', label: '湿度', value: Math.round(a.humidity) + '%' })
  if (a.pressure !== undefined) attrs.push({ key: 'press', label: '气压', value: a.pressure + ' hPa' })
  if (a.wind_speed !== undefined) attrs.push({ key: 'wind', label: '风速', value: a.wind_speed + ' m/s' })
  if (a.visibility !== undefined) attrs.push({ key: 'vis', label: '能见度', value: (a.visibility / 1000).toFixed(1) + ' km' })
  if (a.apparent_temperature !== undefined) attrs.push({ key: 'feels', label: '体感温度', value: Math.round(a.apparent_temperature) + '°' })
  if (a.uv_index !== undefined) attrs.push({ key: 'uv', label: '户外指数', value: a.uv_index })
  if (a.cloud_coverage !== undefined) attrs.push({ key: 'cloud', label: '云量', value: a.cloud_coverage + '%' })
  return attrs
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

const sidebarForecast = computed(() => {
  const fc = props.weatherForecast || []
  return fc.slice(0, 10).map(item => {
    try {
      const dt = new Date(item.datetime)
      return {
        weekday: dt.toLocaleDateString('zh-CN', { weekday: 'short' }),
        condition: item.condition,
        temp: Math.round(item.temperature)
      }
    } catch(e) {
      return { weekday: '?', condition: '', temp: '--' }
    }
  })
})

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
</script>

<style scoped>
.animate-fade-in { animation: fade-in 0.4s ease-out; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.scrollbar-hidden::-webkit-scrollbar { display: none; }
@keyframes bounce-subtle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.animate-bounce-subtle { animation: bounce-subtle 3s ease-in-out infinite; }
</style>
