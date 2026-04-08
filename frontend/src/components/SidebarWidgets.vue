<template>
  <div class="flex flex-col h-full overflow-hidden p-4 space-y-2.5 min-h-0">
    <div class="glass-panel rounded-[1.5rem] p-4 relative overflow-hidden shrink-0 shadow-xl border border-white/10 ring-1 ring-white/10 bg-gradient-to-br from-white/10 to-transparent">
      <div class="flex flex-col items-center">
        <div class="text-6xl font-black tracking-tighter font-heading tabular-nums leading-none mb-1.5 text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.25)]">
          {{ currentTime }}
        </div>
        <div class="text-[10px] font-black uppercase tracking-[0.3em] text-white/20">{{ currentDate }}</div>
      </div>
    </div>

    <div
      v-if="widgets.weather && weatherEntity"
      class="glass-panel rounded-[1.5rem] p-4 relative overflow-hidden group shrink-0 border border-white/5 ring-1 ring-white/10 shadow-lg cursor-pointer active:scale-95 transition-all"
      @click="$emit('open', { type: 'weather', entityId: weatherEntity.entity_id })"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-5xl">{{ weatherEmoji }}</span>
          <div class="flex flex-col">
            <span class="text-3xl font-heading font-black leading-none text-white tracking-tighter">{{ weatherTemperature }}</span>
            <span class="text-[10px] font-black text-cyan-400/60 uppercase tracking-widest">{{ weatherText }}</span>
          </div>
        </div>

        <div class="flex flex-col items-end gap-1">
          <div class="flex gap-1.5 text-xs font-black tabular-nums">
            <span class="text-blue-400">{{ weatherLow }}</span>
            <span class="text-white/20">/</span>
            <span class="text-red-400">{{ weatherHigh }}</span>
          </div>
          <div v-if="weatherHumidity !== '--'" class="text-[9px] font-bold text-white/25 uppercase tracking-widest">
            湿度 {{ weatherHumidity }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="widgets.stats" class="grid grid-cols-2 gap-2.5 shrink-0">
      <div class="glass-panel rounded-[1.25rem] p-3 border border-white/5">
        <div class="text-[10px] font-black uppercase tracking-[0.25em] text-white/20 mb-1">Indoor Temp</div>
        <div class="text-2xl font-heading font-black text-white">{{ indoorTemperature }}</div>
      </div>
      <div class="glass-panel rounded-[1.25rem] p-3 border border-white/5">
        <div class="text-[10px] font-black uppercase tracking-[0.25em] text-white/20 mb-1">Indoor Humidity</div>
        <div class="text-2xl font-heading font-black text-white">{{ indoorHumidity }}</div>
      </div>
    </div>

    <div class="flex flex-row gap-2.5 shrink-0">
      <template v-for="button in activeStatusButtons" :key="button.id">
        <div
          class="glass-panel flex-1 flex flex-col items-center justify-center py-3.5 rounded-[1.5rem] card-hover cursor-pointer border-white/5 ring-1 ring-white/5 relative group transition-all min-w-0 shadow-md"
          @click="$emit('open', { type: button.id, entityId: null })"
        >
          <div class="text-2xl mb-1.5">{{ button.icon }}</div>
          <div class="text-sm font-black leading-none mb-0.5" :class="button.valueClass">{{ button.value }}</div>
          <div class="text-[8px] font-black uppercase tracking-wider text-white/20">{{ button.label }}</div>
          <div v-if="button.active" class="absolute top-2.5 right-2.5 w-1.5 h-1.5 rounded-full shadow-sm" :class="button.indicatorClass"></div>
        </div>
      </template>
    </div>

    <div v-if="widgets.music" class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <MusicAssistantPlayer
        :ma-state="maState"
        :kiosk-mode="kioskMode"
        class="flex-1 min-h-0"
        @select-player="$emit('select-player', $event)"
      />
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
  kioskMode: { type: Boolean, default: false },
  currentTime: { type: String, default: '' },
  currentDate: { type: String, default: '' },
  weatherEntityId: { type: String, default: '' },
  sidebarWidgets: { type: Object, default: () => ({}) },
  selectedLightEntities: { type: Array, default: () => [] },
  selectedClimateEntities: { type: Array, default: () => [] },
  selectedCoverEntities: { type: Array, default: () => [] },
  selectedBatteryEntities: { type: Array, default: () => [] },
  selectedOfflineEntities: { type: Array, default: () => [] }
})

defineEmits(['open', 'select-player'])

const widgets = computed(() => ({
  weather: props.sidebarWidgets.weather !== false,
  stats: props.sidebarWidgets.stats !== false,
  lights: props.sidebarWidgets.lights !== false,
  climate: props.sidebarWidgets.climate !== false,
  battery: props.sidebarWidgets.battery !== false,
  offline: props.sidebarWidgets.offline !== false,
  music: props.sidebarWidgets.music !== false
}))

const filterBySelected = (entities, selectedIds) => {
  if (!Array.isArray(selectedIds) || selectedIds.length === 0) return entities
  const selected = new Set(selectedIds)
  return entities.filter((entity) => selected.has(entity.entity_id))
}

const weatherData = computed(() => props.summary?.weather || {})

const weatherEntity = computed(() => {
  if (props.weatherEntityId) {
    const selected = props.haEntities.find((entity) => entity.entity_id === props.weatherEntityId)
    if (selected) return selected
  }

  return (
    props.haEntities.find((entity) => entity.entity_id.startsWith('weather.') && entity.attributes?.forecast) ||
    props.haEntities.find((entity) => entity.entity_id.startsWith('weather.')) ||
    null
  )
})

const weatherText = computed(() => weatherData.value?.state || weatherEntity.value?.state || '未知')
const weatherTemperature = computed(() => {
  const value = weatherData.value?.temperature ?? weatherEntity.value?.attributes?.temperature
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})
const weatherHumidity = computed(() => {
  const value = weatherData.value?.humidity ?? weatherEntity.value?.attributes?.humidity
  return value !== undefined && value !== null ? `${Math.round(Number(value))}%` : '--'
})
const weatherHigh = computed(() => {
  const firstForecast = weatherData.value?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const value = firstForecast?.temperature ?? firstForecast?.temp_high ?? firstForecast?.max_temp ?? weatherData.value?.temperature_high
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})
const weatherLow = computed(() => {
  const firstForecast = weatherData.value?.forecast?.[0] || weatherEntity.value?.attributes?.forecast?.[0]
  const value = firstForecast?.templow ?? firstForecast?.temperature_low ?? firstForecast?.min_temp ?? weatherData.value?.temperature_low
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})

const indoorTemperature = computed(() => {
  const value = props.summary?.temperature
  return value !== undefined && value !== null ? `${Math.round(Number(value))}°` : '--'
})

const indoorHumidity = computed(() => {
  const value = props.summary?.humidity
  return value !== undefined && value !== null ? `${Math.round(Number(value))}%` : '--'
})

const getWeatherEmoji = (condition) => {
  const normalized = (condition || '').toLowerCase()
  if (normalized.includes('rain')) return '🌧️'
  if (normalized.includes('cloud')) return '☁️'
  if (normalized.includes('sun') || normalized.includes('clear')) return '☀️'
  if (normalized.includes('snow')) return '❄️'
  if (normalized.includes('fog') || normalized.includes('mist')) return '🌫️'
  return '🌤️'
}

const weatherEmoji = computed(() => getWeatherEmoji(weatherText.value))

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

const coverSummary = computed(() => ({
  total: props.summary?.cover_total || filterBySelected(
    props.haEntities.filter((entity) => entity.entity_id.startsWith('cover.')),
    props.selectedCoverEntities
  ).length,
  open: props.summary?.cover_open || 0
}))

const activeStatusButtons = computed(() => {
  const buttons = []

  if (widgets.value.lights) {
    buttons.push({
      id: 'lights',
      label: 'Lights',
      icon: '💡',
      value: `${props.summary.lights_on || 0}/${props.summary.lights_total || 0}`,
      valueClass: 'text-yellow-400',
      active: (props.summary.lights_on || 0) > 0,
      indicatorClass: 'bg-yellow-400'
    })
  }

  if (widgets.value.climate) {
    buttons.push({
      id: 'climate',
      label: 'Climate',
      icon: '❄️',
      value: `${props.summary.climate_active || 0}/${props.summary.climate_total || 0}`,
      valueClass: 'text-cyan-400',
      active: (props.summary.climate_active || 0) > 0,
      indicatorClass: 'bg-cyan-400'
    })
  }

  if (coverSummary.value.total > 0) {
    buttons.push({
      id: 'cover',
      label: 'Curtains',
      icon: '🪟',
      value: `${coverSummary.value.open}/${coverSummary.value.total}`,
      valueClass: 'text-blue-400',
      active: coverSummary.value.open > 0,
      indicatorClass: 'bg-blue-400'
    })
  }

  if (widgets.value.battery) {
    const lowCount = lowBatteryEntities.value.length
    buttons.push({
      id: 'battery',
      label: 'Battery',
      icon: '🔋',
      value: lowCount > 0 ? lowCount : 'OK',
      valueClass: lowCount > 0 ? 'text-red-400' : 'text-emerald-400',
      active: lowCount > 0,
      indicatorClass: 'bg-red-400'
    })
  }

  if (widgets.value.offline) {
    const offlineCount = offlineEntities.value.length
    buttons.push({
      id: 'offline',
      label: 'Offline',
      icon: '📡',
      value: offlineCount > 0 ? offlineCount : 'OK',
      valueClass: offlineCount > 0 ? 'text-orange-400' : 'text-white/30',
      active: offlineCount > 0,
      indicatorClass: 'bg-orange-400'
    })
  }

  return buttons
})
</script>
