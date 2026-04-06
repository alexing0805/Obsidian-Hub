<template>
  <div class="w-full h-full relative overflow-hidden rounded-2xl">

    <!-- 返回总览按钮 -->
    <button v-if="currentView !== 'overview'"
      class="absolute top-3 left-3 z-10 glass-effect rounded-lg px-3 py-1.5 text-xs flex items-center gap-1.5 text-white/60 hover:text-white hover:bg-white/10 transition-colors"
      @click="$emit('set-view', 'overview')">
      ← 返回总览
    </button>

    <!-- 视图标题 -->
    <div v-if="currentView !== 'overview'"
      class="absolute top-3 left-1/2 -translate-x-1/2 z-10 glass-effect rounded-lg px-4 py-1.5 text-sm font-medium">
      {{ viewTitle }}
    </div>

    <!-- 总览：楼层平面图 -->
    <div v-if="currentView === 'overview'" class="absolute inset-0">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950">
        <svg class="w-full h-full" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid meet">
          <rect x="50" y="50" width="700" height="500" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
          <rect x="60" y="60" width="250" height="180" fill="rgba(20,20,30,0.8)" stroke="rgba(255,255,255,0.15)" stroke-width="2" rx="8"/>
          <rect x="490" y="60" width="250" height="180" fill="rgba(20,20,30,0.8)" stroke="rgba(255,255,255,0.15)" stroke-width="2" rx="8"/>
          <rect x="60" y="260" width="680" height="280" fill="rgba(20,20,30,0.8)" stroke="rgba(255,255,255,0.15)" stroke-width="2" rx="8"/>
          <g>
            <circle
              v-for="(light, i) in floorLights"
              :key="light.entity_id"
              :cx="lightPositions[i][0]"
              :cy="lightPositions[i][1]"
              r="11"
              :fill="light.state === 'on' ? '#fbbf24' : 'rgba(255,255,255,0.3)'"
              class="light-dot"
              :style="light.state === 'on' ? 'filter: drop-shadow(0 0 10px rgba(251, 191, 36, 0.65));' : ''"
              @click="$emit('toggle-light', light)"
            />
          </g>
        </svg>
      </div>
      <div class="absolute top-4 left-4 flex gap-3">
        <div class="glass-effect rounded-xl px-4 py-2 text-xs">
          <span class="text-white/60">温度</span>
          <span class="text-white font-bold ml-2">{{ displayTemperature }}</span>
        </div>
        <div class="glass-effect rounded-xl px-4 py-2 text-xs">
          <span class="text-white/60">湿度</span>
          <span class="text-white font-bold ml-2">{{ displayHumidity }}</span>
        </div>
      </div>
      <div class="absolute bottom-4 left-4 right-4">
        <div class="glass-effect rounded-xl px-4 py-2 text-xs text-white/70 truncate">
          <span class="text-white/40 mr-2">灯光映射:</span>
          <span v-if="floorLights.length">{{ floorLights.map((item) => item.attributes?.friendly_name || item.entity_id).join(' / ') }}</span>
          <span v-else>暂无可控灯光（点击侧边栏或设置中添加映射）</span>
        </div>
      </div>
    </div>

    <!-- 灯光视图 -->
    <div v-if="currentView === 'lights'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6 overflow-y-auto">
      <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="light in allLights" :key="light.entity_id"
          class="glass-effect rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer transition-all"
          :class="light.state === 'on' ? 'border border-yellow-500/40 bg-yellow-500/5' : 'border border-white/10 hover:border-white/20'"
          @click="$emit('toggle-light', light)">
          <div class="text-4xl">{{ light.state === 'on' ? '💡' : '🔦' }}</div>
          <div class="text-center">
            <div class="text-sm font-medium truncate max-w-full">{{ light.attributes?.friendly_name || light.entity_id }}</div>
            <div class="text-xs mt-1" :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/40'">
              {{ light.state === 'on' ? '● 已开启' : '○ 已关闭' }}
            </div>
          </div>
          <div class="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div class="h-full bg-yellow-500 rounded-full transition-all" :style="{ width: light.state === 'on' ? '100%' : '20%' }"></div>
          </div>
        </div>
        <div v-if="!allLights.length" class="col-span-full text-center text-white/30 py-20">
          未检测到灯光设备
        </div>
      </div>
    </div>

    <!-- 空调视图 -->
    <div v-if="currentView === 'climate'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6 overflow-y-auto">
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="climate in allClimates" :key="climate.entity_id"
          class="glass-effect rounded-2xl p-5 border border-blue-500/20">
          <div class="flex items-start justify-between mb-4">
            <div>
              <div class="text-lg font-bold">{{ climate.attributes?.friendly_name || climate.entity_id }}</div>
              <div class="text-xs text-white/40 mt-0.5">{{ climate.state }}</div>
            </div>
            <div class="text-3xl">❄️</div>
          </div>
          <div class="flex items-center gap-4 mb-4">
            <div class="text-4xl font-bold text-blue-300">{{ climate.attributes?.temperature || '--' }}°</div>
            <div class="flex-1">
              <div class="text-xs text-white/40 mb-1">目标温度</div>
              <input type="range" min="16" max="30" step="0.5"
                :value="climate.attributes?.temperature || 24"
                class="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-blue-400"
                @change="setClimateTemp(climate, $event.target.value)" />
            </div>
          </div>
          <div class="flex gap-2 flex-wrap">
            <button v-for="mode in ['off','heat','cool','auto']" :key="mode"
              class="px-3 py-1 text-xs rounded-lg border transition-colors"
              :class="climate.state === mode
                ? 'border-blue-500/50 bg-blue-500/20 text-blue-300'
                : 'border-white/10 text-white/40 hover:border-white/20'"
              @click="setClimateMode(climate, mode)">
              {{ modeLabel(mode) }}
            </button>
          </div>
        </div>
        <div v-if="!allClimates.length" class="col-span-full text-center text-white/30 py-20">
          未检测到空调设备
        </div>
      </div>
    </div>

    <!-- 天气视图 -->
    <div v-if="currentView === 'weather'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6">
      <div class="glass-effect rounded-2xl p-8 max-w-md mx-auto border border-white/10">
        <div class="text-center mb-6">
          <div class="text-8xl mb-4">{{ weatherEmoji }}</div>
          <div class="text-6xl font-bold">{{ weatherTemperature }}</div>
          <div class="text-lg text-white/60 mt-1">{{ weatherText }}</div>
          <div class="text-sm text-white/40 mt-1">{{ weatherName }}</div>
        </div>
        <div class="space-y-4">
          <div class="glass-effect rounded-xl p-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-white/60">湿度</span>
              <span class="text-white font-bold">{{ weatherHumidity }}</span>
            </div>
            <div class="h-2 bg-white/10 rounded-full overflow-hidden">
              <div class="h-full bg-cyan-500 rounded-full" :style="{ width: weatherHumidityPercent + '%' }"></div>
            </div>
          </div>
          <div class="glass-effect rounded-xl p-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-white/60">降水量</span>
              <span class="text-white font-bold">{{ weatherPrecipitation }}</span>
            </div>
            <div class="h-2 bg-white/10 rounded-full overflow-hidden">
              <div class="h-full bg-blue-400 rounded-full" :style="{ width: weatherPrecipitationPercent + '%' }"></div>
            </div>
          </div>
          <div class="text-center text-xs text-white/30 mt-4">
            实体: {{ weatherEntityId || '自动' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 音乐视图 -->
    <div v-if="currentView === 'music'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6 overflow-y-auto">
      <MusicAssistantPlayer :ma-state="maState" class="glass-effect rounded-2xl p-6 border border-purple-500/20" />
    </div>

    <!-- 低电量视图 -->
    <div v-if="currentView === 'battery'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6 overflow-y-auto">
      <div class="space-y-3 max-w-xl mx-auto">
        <div v-for="entity in lowBatteryEntities" :key="entity.entity_id"
          class="glass-effect rounded-xl p-4 border border-red-500/20 flex items-center justify-between">
          <div>
            <div class="text-sm font-medium">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
            <div class="text-xs text-white/40 mt-0.5">{{ entity.entity_id }}</div>
          </div>
          <div class="text-2xl font-bold text-red-400">{{ entity.state }}%</div>
        </div>
        <div v-if="!lowBatteryEntities.length" class="text-center text-white/30 py-20">
          🎉 没有低电量设备，电量充足
        </div>
      </div>
    </div>

    <!-- 离线设备视图 -->
    <div v-if="currentView === 'offline'" class="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-950 p-6 overflow-y-auto">
      <div class="space-y-3 max-w-xl mx-auto">
        <div v-for="entity in offlineEntities" :key="entity.entity_id"
          class="glass-effect rounded-xl p-4 border border-orange-500/20 flex items-center justify-between">
          <div>
            <div class="text-sm font-medium">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
            <div class="text-xs text-white/40 mt-0.5">{{ entity.entity_id }}</div>
          </div>
          <div class="text-orange-400 text-sm">📡 离线</div>
        </div>
        <div v-if="!offlineEntities.length" class="text-center text-white/30 py-20">
          ✅ 所有设备在线，无离线设备
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import MusicAssistantPlayer from './MusicAssistantPlayer.vue'

const props = defineProps({
  currentView: { type: String, default: 'overview' },
  haEntities: { type: Array, default: () => [] },
  maState: { type: Object, default: () => ({}) },
  displayTemperature: { type: String, default: '--' },
  displayHumidity: { type: String, default: '--' },
  weatherEntityId: { type: String, default: '' },
  lightPositions: { type: Array, default: () => [] },
})

const emit = defineEmits(['set-view', 'toggle-light', 'climate-temp', 'climate-mode'])

const viewTitle = computed(() => ({
  lights: '💡 灯光控制',
  climate: '❄️ 空调控制',
  weather: '🌤️ 天气',
  music: '🎵 音乐播放',
  battery: '🔋 低电量设备',
  offline: '📡 离线设备',
}[props.currentView] || ''))

const allLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')))
const allClimates = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('climate.')))
const floorLights = computed(() =>
  props.haEntities.filter(e => e.entity_id.startsWith('light.')).slice(0, props.lightPositions.length)
)
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
const weatherText = computed(() => weatherEntity.value?.state || '未知')
const weatherName = computed(() => weatherEntity.value?.attributes?.friendly_name || '天气')
const weatherTemperature = computed(() => {
  const v = weatherEntity.value?.attributes?.temperature
  return v !== undefined && v !== null ? `${Number(v).toFixed(1)}°` : '--'
})
const weatherHumidity = computed(() => {
  const v = weatherEntity.value?.attributes?.humidity
  return v !== undefined && v !== null ? `${Math.round(Number(v))}%` : '--'
})
const weatherPrecipitation = computed(() => {
  const v = weatherEntity.value?.attributes?.precipitation
  return v !== undefined && v !== null ? `${Number(v).toFixed(1)} mm` : '0 mm'
})
const weatherHumidityPercent = computed(() => Math.max(0, Math.min(100, Number(weatherEntity.value?.attributes?.humidity ?? 0))))
const weatherPrecipitationPercent = computed(() => Math.max(0, Math.min(100, Number(weatherEntity.value?.attributes?.precipitation ?? 0) * 10)))
const weatherEmoji = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  return '🌤️'
})

const setClimateTemp = (entity, temp) => emit('climate-temp', { entity, temp })
const setClimateMode = (entity, mode) => emit('climate-mode', { entity, mode })
const modeLabel = (m) => ({ off: '关', heat: '加热', cool: '制冷', auto: '自动', fan_only: '送风', dry: '除湿' }[m] || m)
</script>
