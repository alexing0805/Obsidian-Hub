<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-6 md:p-8" @click.self="$emit('close')">
    <div class="absolute inset-0 bg-black/55 backdrop-blur-md" @click="$emit('close')"></div>

    <div
      class="relative glass-panel rounded-[2.5rem] w-full flex flex-col overflow-hidden shadow-[0_30px_60px_-15px_rgba(0,0,0,0.5)] border-white/10 ring-1 ring-white/5 animate-fade-in"
      :class="type === 'weather' ? 'max-w-4xl max-h-[88vh]' : 'max-w-5xl max-h-[88vh]'"
    >
      <div class="flex items-center justify-between px-8 py-5 border-b border-white/5 shrink-0 bg-white/5">
        <div class="flex items-center gap-4 text-2xl font-extrabold font-heading tracking-tight text-white/90">
          <span class="opacity-80">{{ titleIcon }}</span>
          <span>{{ titleText }}</span>
        </div>
        <button
          class="w-12 h-12 rounded-2xl flex items-center justify-center text-white/30 hover:text-white hover:bg-white/10 transition-all active:scale-90 bg-white/5 border border-white/5"
          @click="$emit('close')"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="type === 'lights'">
          <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              v-for="light in displayLights"
              :key="light.entity_id"
              class="glass-effect rounded-2xl p-5 flex flex-col items-center gap-3 transition-all border text-left"
              :class="light.state === 'on' ? 'border-yellow-500/40 bg-yellow-500/5' : 'border-white/10 hover:border-white/20'"
              @click="toggleLight(light)"
            >
              <div class="text-4xl">{{ light.state === 'on' ? '💡' : '🔅' }}</div>
              <div class="text-sm text-center text-white/70 truncate w-full">
                {{ light.attributes?.friendly_name || light.entity_id }}
              </div>
              <div class="text-sm" :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
                {{ light.state === 'on' ? '已开启' : '已关闭' }}
              </div>
            </button>
          </div>
          <div v-if="!displayLights.length" class="text-center text-white/30 py-16">没有可展示的灯光快捷项</div>
        </div>

        <div v-else-if="type === 'climate'">
          <div v-if="displayClimates.length" class="space-y-6">
            <div
              v-for="climate in displayClimates"
              :key="climate.entity_id"
              class="glass-panel rounded-[2rem] p-6 border border-white/5 bg-gradient-to-br from-white/[0.03] to-transparent shadow-2xl relative overflow-hidden"
            >
              <div class="flex items-center justify-between mb-8">
                <div>
                  <div class="text-xl font-black tracking-tight text-white/90">{{ climate.attributes?.friendly_name || '空调' }}</div>
                  <div class="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400/60 mt-1">{{ climate.state }}</div>
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
                <button
                  class="w-14 h-14 rounded-full flex items-center justify-center border border-white/10 bg-white/5 text-2xl font-black text-white/40 hover:text-white hover:border-white/30 hover:scale-110 active:scale-90 transition-all shadow-lg"
                  @click="setTemp(climate, (climate.attributes?.temperature || 24) - 0.5)"
                >
                  -
                </button>
                <div class="text-6xl font-black tracking-tighter text-white tabular-nums leading-none">
                  {{ Math.round(climate.attributes?.temperature || 24) }}<span class="text-2xl align-top mt-4 ml-0.5">°</span>
                </div>
                <button
                  class="w-14 h-14 rounded-full flex items-center justify-center border border-white/10 bg-white/5 text-2xl font-black text-white/40 hover:text-white hover:border-white/30 hover:scale-110 active:scale-90 transition-all shadow-lg"
                  @click="setTemp(climate, (climate.attributes?.temperature || 24) + 0.5)"
                >
                  +
                </button>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
                <div class="space-y-3">
                  <div class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] ml-2">模式</div>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="mode in getHvacModes(climate)"
                      :key="mode.value"
                      class="flex-1 min-w-[72px] px-3 py-2.5 text-[10px] font-black rounded-xl border transition-all uppercase tracking-wider"
                      :class="climate.state === mode.value ? 'border-blue-500/50 bg-blue-500/20 text-blue-400' : 'border-white/5 bg-white/[0.02] text-white/40'"
                      @click="setMode(climate, mode.value)"
                    >
                      <div class="text-lg mb-0.5">{{ mode.icon }}</div>
                      {{ mode.label }}
                    </button>
                  </div>
                </div>
                <div class="space-y-3">
                  <div class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] ml-2">风速</div>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="fan in getFanModes(climate)"
                      :key="fan"
                      class="flex-1 min-w-[60px] px-3 py-2.5 text-[10px] font-black rounded-xl border transition-all uppercase tracking-tighter"
                      :class="climate.attributes?.fan_mode === fan ? 'border-cyan-500/50 bg-cyan-500/20 text-cyan-400' : 'border-white/5 bg-white/[0.02] text-white/40'"
                      @click="setFanMode(climate, fan)"
                    >
                      <div class="text-lg mb-0.5">🌀</div>
                      {{ fan }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center text-white/30 py-20">没有可展示的空调快捷项</div>
        </div>

        <div v-else-if="type === 'cover'">
          <div v-if="displayCovers.length" class="grid grid-cols-1 xl:grid-cols-2 gap-5">
            <div
              v-for="cover in displayCovers"
              :key="cover.entity_id"
              class="glass-panel p-6 rounded-[2rem] border border-white/5 bg-white/5"
            >
              <div class="flex items-center justify-between mb-5">
                <div>
                  <h3 class="text-xl font-black text-white tracking-tight">{{ cover.attributes?.friendly_name || cover.entity_id }}</h3>
                  <p class="text-[10px] font-black uppercase tracking-[0.35em] text-blue-400/60 mt-1">
                    {{ coverStateLabel(cover.state) }}
                  </p>
                </div>
                <div class="text-4xl">🪟</div>
              </div>

              <div class="grid grid-cols-3 gap-3 mb-5">
                <button
                  class="flex flex-col items-center gap-2 p-4 rounded-[1.4rem] glass-effect border border-white/5 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all"
                  @click="emitCoverService(cover, 'open_cover')"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7" />
                  </svg>
                  <span class="text-[10px] font-black uppercase tracking-widest text-white/50">开启</span>
                </button>
                <button
                  class="flex flex-col items-center gap-2 p-4 rounded-[1.4rem] glass-effect border border-white/5 hover:border-white/30 hover:bg-white/10 transition-all"
                  @click="emitCoverService(cover, 'stop_cover')"
                >
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12" rx="2" />
                  </svg>
                  <span class="text-[10px] font-black uppercase tracking-widest text-white/50">停止</span>
                </button>
                <button
                  class="flex flex-col items-center gap-2 p-4 rounded-[1.4rem] glass-effect border border-white/5 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all"
                  @click="emitCoverService(cover, 'close_cover')"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                  </svg>
                  <span class="text-[10px] font-black uppercase tracking-widest text-white/50">关闭</span>
                </button>
              </div>

              <div class="rounded-[1.5rem] border border-white/5 bg-black/15 p-4">
                <div class="flex justify-between items-center mb-3">
                  <span class="text-[10px] font-black uppercase tracking-[0.25em] text-white/30">位置</span>
                  <span class="text-xl font-black text-blue-400 tabular-nums">{{ getCoverPosition(cover) }}%</span>
                </div>
                <input
                  :value="getCoverPosition(cover)"
                  type="range"
                  min="0"
                  max="100"
                  class="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer accent-blue-500"
                  @change="onCoverPositionChange(cover, $event)"
                />
              </div>
            </div>
          </div>
          <div v-else class="text-center text-white/30 py-20">没有可展示的窗帘快捷项</div>
        </div>

        <div v-else-if="type === 'weather'">
          <div v-if="weatherEntity" class="space-y-4">
            <div class="flex items-center justify-between bg-white/5 rounded-[2rem] p-6 border border-white/10 shadow-inner">
              <div class="flex items-center gap-6">
                <div class="text-7xl">{{ weatherEmoji }}</div>
                <div class="flex flex-col">
                  <div class="text-3xl font-black text-white leading-tight">{{ weatherText }}</div>
                  <div class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mt-1">天气概览</div>
                </div>
              </div>
              <div class="flex flex-col items-end">
                <div class="text-5xl font-black text-white tracking-tighter leading-none mb-1">{{ weatherTemperature }}</div>
                <div class="flex gap-1 text-sm font-black tabular-nums">
                  <span class="text-blue-400">{{ weatherLow }}</span>
                  <span class="text-white/40">/</span>
                  <span class="text-red-400">{{ weatherHigh }}</span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div
                v-for="attr in weatherAttrs"
                :key="attr.key"
                class="glass-panel p-3.5 rounded-2xl flex flex-col items-center justify-center border border-white/5 bg-white/5"
              >
                <div class="text-xl mb-1 opacity-80">{{ attr.icon }}</div>
                <div class="text-[9px] font-black text-white/20 uppercase tracking-widest mb-0.5">{{ attr.label }}</div>
                <div class="text-sm font-black text-white">{{ attr.value }}</div>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center gap-1 p-1 bg-black/20 rounded-xl w-fit mx-auto border border-white/5">
                <button
                  v-for="mode in ['daily', 'hourly']"
                  :key="mode"
                  class="px-5 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all"
                  :class="forecastMode === mode ? 'bg-white/10 text-cyan-400 shadow-lg' : 'text-white/40 hover:text-white/60'"
                  @click="forecastMode = mode"
                >
                  {{ mode === 'daily' ? '每日' : '每小时' }}
                </button>
              </div>

              <div v-if="forecastMode === 'daily'" class="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hidden">
                <div
                  v-for="(fc, idx) in dailyForecast"
                  :key="idx"
                  class="flex-shrink-0 w-24 glass-panel p-4 rounded-[1.5rem] flex flex-col items-center border border-white/5 bg-gradient-to-b from-white/5 to-transparent"
                >
                  <span class="text-[10px] font-black text-white/30 uppercase mb-2 tracking-wider">{{ fc.weekday }}</span>
                  <span class="text-3xl mb-3">{{ weatherEmojiFor(fc.condition) }}</span>
                  <div class="flex flex-col items-center gap-0.5">
                    <span class="text-sm font-black text-white">{{ fc.tempHigh }}</span>
                    <span class="text-[10px] font-bold text-white/20">{{ fc.tempLow }}</span>
                  </div>
                </div>
              </div>

              <div v-else class="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hidden">
                <div
                  v-for="(fc, idx) in hourlyForecast"
                  :key="idx"
                  class="flex-shrink-0 w-20 glass-panel p-4 rounded-[1.5rem] flex flex-col items-center border border-white/5 bg-gradient-to-b from-white/5 to-transparent"
                >
                  <span class="text-[10px] font-black text-white/30 uppercase mb-2 tracking-wider">{{ fc.hour }}</span>
                  <span class="text-2xl mb-2">{{ weatherEmojiFor(fc.condition) }}</span>
                  <span class="text-sm font-black text-white">{{ fc.temp }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="type === 'battery'">
          <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="battery in lowBatteryEntities"
              :key="battery.entity_id"
              class="glass-effect rounded-2xl p-5 flex flex-col items-center gap-3 border"
              :class="parseFloat(battery.state) <= 10 ? 'border-red-500/40 bg-red-500/5' : 'border-yellow-500/40 bg-yellow-500/5'"
            >
              <div class="text-4xl">{{ parseFloat(battery.state) <= 10 ? '🪫' : '🔋' }}</div>
              <div class="text-sm text-center text-white/70 truncate w-full">{{ battery.attributes?.friendly_name || battery.entity_id }}</div>
              <div class="text-xl font-black text-white">{{ battery.state }}%</div>
            </div>
          </div>
          <div v-if="!lowBatteryEntities.length" class="text-center text-white/30 py-16">当前没有低电量设备</div>
        </div>

        <div v-else-if="type === 'offline'">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div
              v-for="entity in offlineEntities"
              :key="entity.entity_id"
              class="glass-effect rounded-2xl p-5 flex items-center gap-4 border border-orange-500/20 bg-orange-500/5"
            >
              <div class="text-3xl">📡</div>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white/70 truncate">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
                <div class="text-xs text-orange-400/60 uppercase">{{ entity.state }}</div>
              </div>
            </div>
          </div>
          <div v-if="!offlineEntities.length" class="text-center text-white/30 py-16">当前没有离线设备</div>
        </div>

        <div v-else-if="type === 'sensor'">
          <div v-if="sensorEntity" class="max-w-lg mx-auto glass-panel rounded-[2rem] p-6 border border-white/5 bg-white/5">
            <div class="text-3xl mb-4 text-center">🌡️</div>
            <div class="text-xl font-black text-center text-white mb-2">{{ sensorEntity.attributes?.friendly_name || sensorEntity.entity_id }}</div>
            <div class="text-5xl font-black text-center text-cyan-400 mb-2">
              {{ sensorEntity.state }}{{ sensorEntity.attributes?.unit_of_measurement || '' }}
            </div>
            <div class="text-center text-xs uppercase tracking-[0.25em] text-white/25">{{ sensorEntity.entity_id }}</div>
          </div>
        </div>

        <div v-else-if="type === 'music'">
          <MusicAssistantPlayer :ma-state="maState" :kiosk-mode="kioskMode" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'

const props = defineProps({
  type: { type: String, default: '' },
  entityId: { type: String, default: null },
  haEntities: { type: Array, default: () => [] },
  maState: { type: Object, default: () => ({}) },
  kioskMode: { type: Boolean, default: false },
  weatherEntityId: { type: String, default: '' },
  summary: { type: Object, default: () => ({}) },
  selectedLightEntities: { type: Array, default: () => [] },
  selectedClimateEntities: { type: Array, default: () => [] },
  selectedCoverEntities: { type: Array, default: () => [] },
  selectedBatteryEntities: { type: Array, default: () => [] },
  selectedOfflineEntities: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'toggle-light', 'climate-action', 'cover-action'])

const filterBySelected = (entities, selectedIds) => {
  if (!Array.isArray(selectedIds) || selectedIds.length === 0) return entities
  const selected = new Set(selectedIds)
  return entities.filter((entity) => selected.has(entity.entity_id))
}

const titleMap = {
  lights: { icon: '💡', text: '灯光快捷' },
  climate: { icon: '❄️', text: '空调快捷' },
  weather: { icon: '🌤️', text: '天气详情' },
  battery: { icon: '🔋', text: '低电量设备' },
  offline: { icon: '📡', text: '离线设备' },
  music: { icon: '🎵', text: '音乐播放' },
  cover: { icon: '🪟', text: '窗帘快捷' },
  sensor: { icon: '🌡️', text: '传感器' }
}

const titleIcon = computed(() => titleMap[props.type]?.icon || '')
const titleText = computed(() => titleMap[props.type]?.text || '')
const forecastMode = ref('daily')

const displayLights = computed(() => {
  const all = filterBySelected(
    props.haEntities.filter((entity) => entity.entity_id.startsWith('light.')),
    props.selectedLightEntities
  )
  if (props.entityId) return all.filter((entity) => entity.entity_id === props.entityId)
  return all
})

const displayClimates = computed(() => {
  const all = filterBySelected(
    props.haEntities.filter((entity) => entity.entity_id.startsWith('climate.')),
    props.selectedClimateEntities
  )
  if (props.entityId) return all.filter((entity) => entity.entity_id === props.entityId)
  return all
})

const displayCovers = computed(() => {
  const all = filterBySelected(
    props.haEntities.filter((entity) => entity.entity_id.startsWith('cover.')),
    props.selectedCoverEntities
  )
  if (props.entityId) return all.filter((entity) => entity.entity_id === props.entityId)
  return all
})

const sensorEntity = computed(() => props.haEntities.find((entity) => entity.entity_id === props.entityId) || null)

const lowBatteryEntities = computed(() =>
  filterBySelected(
    props.haEntities.filter((entity) => {
      if (entity.attributes?.device_class !== 'battery') return false
      const value = parseFloat(entity.state)
      return !Number.isNaN(value) && value <= 20
    }),
    props.selectedBatteryEntities
  )
)

const offlineEntities = computed(() =>
  filterBySelected(
    props.haEntities.filter((entity) =>
      ['unknown', 'unavailable', 'none', ''].includes(String(entity.state).toLowerCase())
    ),
    props.selectedOfflineEntities
  )
)

const weatherEntity = computed(() => {
  if (props.weatherEntityId) {
    const selected = props.haEntities.find((entity) => entity.entity_id === props.weatherEntityId)
    if (selected) return selected
  }
  return props.haEntities.find((entity) => entity.entity_id.startsWith('weather.')) || null
})

const weatherText = computed(() => props.summary?.weather?.state || weatherEntity.value?.state || '未知')
const weatherTemperature = computed(() => {
  const value = props.summary?.weather?.temperature ?? weatherEntity.value?.attributes?.temperature
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})
const weatherLow = computed(() => {
  const fc0 = props.summary?.weather?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const value = fc0?.templow ?? fc0?.temperature_low ?? fc0?.min_temp ?? props.summary?.weather?.temperature_low
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})
const weatherHigh = computed(() => {
  const fc0 = props.summary?.weather?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const value = fc0?.temperature ?? fc0?.temp_high ?? fc0?.max_temp ?? props.summary?.weather?.temperature_high
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})

const weatherEmojiFor = (condition) => {
  const state = String(condition || '').toLowerCase()
  if (state.includes('rain')) return '🌧️'
  if (state.includes('cloud')) return '☁️'
  if (state.includes('sun') || state.includes('clear')) return '☀️'
  if (state.includes('snow')) return '❄️'
  if (state.includes('fog') || state.includes('mist')) return '🌫️'
  return '🌤️'
}

const weatherEmoji = computed(() => weatherEmojiFor(weatherText.value))

const weatherAttrs = computed(() => {
  if (!weatherEntity.value) return []
  const attrs = weatherEntity.value.attributes || {}
  const summaryWeather = props.summary?.weather || {}
  return [
    { key: 'pressure', label: '气压', value: `${summaryWeather.pressure ?? attrs.pressure ?? '--'} hPa`, icon: '🧭' },
    { key: 'humidity', label: '湿度', value: `${summaryWeather.humidity ?? attrs.humidity ?? '--'}%`, icon: '💧' },
    { key: 'wind_speed', label: '风速', value: `${summaryWeather.wind_speed ?? attrs.wind_speed ?? '--'} km/h`, icon: '🌀' },
    { key: 'visibility', label: '能见度', value: `${summaryWeather.visibility ?? attrs.visibility ?? '--'} km`, icon: '👁️' }
  ]
})

const dailyForecast = computed(() => {
  const forecast = props.summary?.weather?.forecast || weatherEntity.value?.attributes?.forecast || []
  return forecast.slice(0, 7).map((item) => {
    const high = item.temperature ?? item.temp_high ?? item.max_temp
    const low = item.templow ?? item.temperature_low ?? item.min_temp
    return {
      weekday: item.datetime ? new Date(item.datetime).toLocaleDateString('zh-CN', { weekday: 'short' }) : '--',
      condition: item.condition,
      tempHigh: high !== undefined && high !== null ? `${Math.round(Number(high))}°` : '--',
      tempLow: low !== undefined && low !== null ? `${Math.round(Number(low))}°` : '--'
    }
  })
})

const hourlyForecast = computed(() => {
  const forecast = props.summary?.weather?.hourly_forecast || []
  return forecast.slice(0, 24).map((item) => ({
    hour: item.datetime ? `${String(new Date(item.datetime).getHours()).padStart(2, '0')}:00` : '--',
    condition: item.condition,
    temp: item.temperature !== undefined && item.temperature !== null ? `${Math.round(Number(item.temperature))}°` : '--'
  }))
})

const getHvacModes = (climate) => {
  const modes = climate.attributes?.hvac_modes || ['off', 'heat', 'cool', 'auto', 'dry', 'fan_only']
  const map = {
    off: { label: '关闭', icon: '⭘' },
    heat: { label: '制热', icon: '🔥' },
    cool: { label: '制冷', icon: '❄️' },
    auto: { label: '自动', icon: '🤖' },
    dry: { label: '除湿', icon: '💧' },
    fan_only: { label: '送风', icon: '🌀' }
  }
  return modes.map((mode) => map[mode] ? { ...map[mode], value: mode } : { value: mode, label: mode.toUpperCase(), icon: '⚙️' })
}

const getFanModes = (climate) => climate.attributes?.fan_mode_list || climate.attributes?.fan_modes || ['low', 'medium', 'high', 'auto']

const toggleLight = (entity) => emit('toggle-light', entity)
const setTemp = (entity, temp) => emit('climate-action', { entity, action: 'temp', value: temp })
const setMode = (entity, mode) => emit('climate-action', { entity, action: 'mode', value: mode })
const setFanMode = (entity, fan) => emit('climate-action', { entity, action: 'fan', value: fan })

const getCoverPosition = (cover) => {
  const position = Number(cover.attributes?.current_position)
  return Number.isFinite(position) ? position : (String(cover.state).toLowerCase() === 'open' ? 100 : 0)
}

const coverStateLabel = (state) => {
  const value = String(state || '').toLowerCase()
  if (value === 'open') return '已开启'
  if (value === 'closed') return '已关闭'
  return state || '--'
}

const emitCoverService = (cover, service) => {
  emit('cover-action', { service, entityId: cover.entity_id })
}

const onCoverPositionChange = (cover, event) => {
  emit('cover-action', {
    service: 'set_cover_position',
    entityId: cover.entity_id,
    data: { position: parseInt(event.target.value, 10) }
  })
}
</script>

<style scoped>
.animate-fade-in {
  animation: fade-in 0.35s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}
</style>
