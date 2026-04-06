<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-6 md:p-12" @click.self="$emit('close')">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-md transition-all duration-500" @click="$emit('close')"></div>
 
    <div class="relative glass-panel rounded-[2.5rem] w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden shadow-[0_30px_60px_-15px_rgba(0,0,0,0.5)] border-white/10 ring-1 ring-white/5 animate-fade-in">
 
      <!-- 标题栏 -->
      <div class="flex items-center justify-between px-8 py-5 border-b border-white/5 shrink-0 bg-white/5">
        <div class="flex items-center gap-3 text-xl font-extrabold font-heading tracking-tight text-white/90">
          <span class="opacity-80">{{ titleIcon }}</span>
          <span>{{ titleText }}</span>
        </div>
        <button class="w-10 h-10 rounded-2xl flex items-center justify-center text-white/30 hover:text-white hover:bg-white/10 transition-all active:scale-90 bg-white/5 border border-white/5"
          @click="$emit('close')">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 overflow-y-auto p-5">

        <!-- 灯光详情 -->
        <div v-if="type === 'lights'">
          <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div v-for="light in allLights" :key="light.entity_id"
              class="glass-effect rounded-xl p-4 flex flex-col items-center gap-2 cursor-pointer transition-all border"
              :class="light.state === 'on' ? 'border-yellow-500/40 bg-yellow-500/5' : 'border-white/10 hover:border-white/20'"
              @click="toggleLight(light)">
              <div class="text-3xl">{{ light.state === 'on' ? '💡' : '🔦' }}</div>
              <div class="text-xs text-center text-white/70 truncate w-full">
                {{ light.attributes?.friendly_name || light.entity_id }}
              </div>
              <div class="text-xs" :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
                {{ light.state === 'on' ? '● 已开启' : '○ 已关闭' }}
              </div>
            </div>
          </div>
          <div v-if="!allLights.length" class="text-center text-white/30 py-10">未检测到灯光设备</div>
        </div>

        <!-- 空调详情 -->
        <div v-if="type === 'climate'">
          <div class="space-y-4">
            <div v-for="climate in allClimates" :key="climate.entity_id"
              class="glass-effect rounded-2xl p-5 border border-blue-500/20">

              <!-- 设备名 -->
              <div class="flex items-center justify-between mb-4">
                <div class="font-medium">{{ climate.attributes?.friendly_name || climate.entity_id }}</div>
                <div class="text-sm text-blue-300">{{ climate.state }}</div>
              </div>

              <!-- 当前温度 + 目标温度 -->
              <div class="flex items-center gap-4 mb-4">
                <div class="text-4xl font-bold text-blue-300">
                  {{ climate.attributes?.current_temperature !== undefined ? climate.attributes.current_temperature + '°' : '--' }}
                </div>
                <div class="flex-1">
                  <div class="text-xs text-white/40 mb-1">目标温度</div>
                  <input type="range" min="16" max="32" step="0.5"
                    :value="climate.attributes?.temperature || 24"
                    class="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-blue-400"
                    @change="setTemp(climate, $event.target.value)" />
                  <div class="text-center text-sm text-blue-300 mt-1">{{ climate.attributes?.temperature || '--' }}°C</div>
                </div>
              </div>

              <!-- HVAC 模式 -->
              <div class="mb-3">
                <div class="text-xs text-white/40 mb-2">模式</div>
                <div class="flex flex-wrap gap-2">
                  <button v-for="mode in hvacModes" :key="mode.value"
                    class="px-3 py-1.5 text-xs rounded-lg border transition-colors"
                    :class="climate.attributes?.hvac_modes?.includes(mode.value) && climate.state === mode.value
                      ? 'border-blue-500/50 bg-blue-500/20 text-blue-300'
                      : 'border-white/10 text-white/40 hover:border-white/20'"
                    :disabled="!climate.attributes?.hvac_modes?.includes(mode.value)"
                    @click="setMode(climate, mode.value)">
                    {{ mode.icon }} {{ mode.label }}
                  </button>
                </div>
              </div>

              <!-- 风扇速度 -->
              <div class="mb-3">
                <div class="text-xs text-white/40 mb-2">风速</div>
                <div class="flex flex-wrap gap-2">
                  <button v-for="fan in fanSpeeds" :key="fan.value"
                    class="px-3 py-1.5 text-xs rounded-lg border transition-colors"
                    :class="climate.attributes?.fan_mode === fan.value
                      ? 'border-cyan-500/50 bg-cyan-500/20 text-cyan-300'
                      : 'border-white/10 text-white/40 hover:border-white/20'"
                    @click="setFanMode(climate, fan.value)">
                    {{ fan.icon }} {{ fan.label }}
                  </button>
                </div>
              </div>

              <!-- 摆风 -->
              <div v-if="climate.attributes?.swing_modes?.length">
                <div class="text-xs text-white/40 mb-2">摆风</div>
                <div class="flex flex-wrap gap-2">
                  <button v-for="swing in (climate.attributes.swing_modes || [])" :key="swing"
                    class="px-3 py-1.5 text-xs rounded-lg border transition-colors"
                    :class="climate.attributes?.swing_mode === swing
                      ? 'border-green-500/50 bg-green-500/20 text-green-300'
                      : 'border-white/10 text-white/40 hover:border-white/20'"
                    @click="setSwing(climate, swing)">
                    {{ swing }}
                  </button>
                </div>
              </div>

            </div>
          </div>
          <div v-if="!allClimates.length" class="text-center text-white/30 py-10">未检测到空调设备</div>
        </div>

        <!-- 天气详情 -->
        <div v-if="type === 'weather'">
          <div v-if="weatherEntity" class="space-y-4">
            <div class="text-center mb-6">
              <div class="text-8xl mb-3">{{ weatherEmoji }}</div>
              <div class="text-5xl font-bold">{{ weatherTemperature }}</div>
              <div class="text-lg text-white/60 mt-1">{{ weatherEntity.state }}</div>
              <div class="text-sm text-white/40 mt-1">{{ weatherEntity.attributes?.friendly_name }}</div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="attr in weatherAttrs" :key="attr.key"
                class="glass-effect rounded-xl p-4 text-center">
                <div class="text-xs text-white/40 mb-1">{{ attr.label }}</div>
                <div class="text-lg font-bold">{{ attr.value }}</div>
              </div>
            </div>
          </div>
          <div v-else class="text-center text-white/30 py-10">未检测到天气实体</div>
        </div>

        <!-- 低电量 -->
        <div v-if="type === 'battery'">
          <div class="space-y-2">
            <div v-for="entity in lowBatteryEntities" :key="entity.entity_id"
              class="glass-effect rounded-xl p-4 flex items-center justify-between border border-red-500/20">
              <div>
                <div class="text-sm font-medium">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
                <div class="text-xs text-white/40 font-mono mt-0.5">{{ entity.entity_id }}</div>
              </div>
              <div class="flex items-center gap-3">
                <div class="h-2 w-24 bg-white/10 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :style="{ width: entity.state + '%', background: batteryColor(entity.state) }"></div>
                </div>
                <span class="text-xl font-bold text-red-400">{{ entity.state }}%</span>
              </div>
            </div>
          </div>
          <div v-if="!lowBatteryEntities.length" class="text-center text-emerald-400 py-10 text-lg">🎉 所有设备电量充足</div>
        </div>

        <!-- 离线设备 -->
        <div v-if="type === 'offline'">
          <div class="space-y-2">
            <div v-for="entity in offlineEntities" :key="entity.entity_id"
              class="glass-effect rounded-xl p-4 flex items-center justify-between border border-orange-500/20">
              <div>
                <div class="text-sm font-medium">{{ entity.attributes?.friendly_name || entity.entity_id }}</div>
                <div class="text-xs text-white/40 font-mono mt-0.5">{{ entity.entity_id }}</div>
              </div>
              <span class="text-orange-400 text-sm">📡 离线</span>
            </div>
          </div>
          <div v-if="!offlineEntities.length" class="text-center text-emerald-400 py-10 text-lg">✅ 所有设备在线</div>
        </div>

        <!-- 音乐 -->
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
  type: { type: String, default: '' },  // lights | climate | weather | battery | offline | music
  haEntities: { type: Array, default: () => [] },
  maState: { type: Object, default: () => ({}) },
  weatherEntityId: { type: String, default: '' },
})

const emit = defineEmits(['close', 'toggle-light', 'climate-action'])

const titleMap = {
  lights: { icon: '💡', text: 'LIGHTING' },
  climate: { icon: '❄️', text: 'CLIMATE' },
  weather: { icon: '🌤️', text: 'WEATHER' },
  battery: { icon: '🔋', text: 'BATTERY' },
  offline: { icon: '📡', text: 'OFFLINE' },
  music: { icon: '🎵', text: 'MUSIC' },
}
const titleIcon = computed(() => titleMap[props.type]?.icon || '')
const titleText = computed(() => titleMap[props.type]?.text || '')

const allLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')))
const allClimates = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('climate.')))
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
  if (s.includes('thunder')) return '⛈️'
  return '🌤️'
})
const weatherAttrs = computed(() => {
  const a = weatherEntity.value?.attributes || {}
  const attrs = []
  if (a.humidity !== undefined) attrs.push({ key: 'humidity', label: '湿度', value: Math.round(a.humidity) + '%' })
  if (a.pressure !== undefined) attrs.push({ key: 'pressure', label: '气压', value: a.pressure + ' hPa' })
  if (a.wind_speed !== undefined) attrs.push({ key: 'wind', label: '风速', value: a.wind_speed + ' m/s' })
  if (a.precipitation !== undefined) attrs.push({ key: 'precip', label: '降水量', value: a.precipitation + ' mm' })
  if (a.precipitation_probability !== undefined) attrs.push({ key: 'pop', label: '降水概率', value: a.precipitation_probability + '%' })
  if (a.visibility !== undefined) attrs.push({ key: 'vis', label: '能见度', value: (a.visibility / 1000).toFixed(1) + ' km' })
  if (a.cloud_coverage !== undefined) attrs.push({ key: 'cloud', label: '云量', value: a.cloud_coverage + '%' })
  if (a.uv_index !== undefined) attrs.push({ key: 'uv', label: '紫外线指数', value: a.uv_index })
  if (a.apparent_temperature !== undefined) attrs.push({ key: 'feels', label: '体感温度', value: a.apparent_temperature + '°' })
  return attrs
})

const hvacModes = [
  { value: 'off', label: '关', icon: '⭕' },
  { value: 'heat', label: '加热', icon: '🔥' },
  { value: 'cool', label: '制冷', icon: '❄️' },
  { value: 'auto', label: '自动', icon: '🔄' },
  { value: 'dry', label: '除湿', icon: '💧' },
  { value: 'fan_only', label: '送风', icon: '🌬️' },
]
const fanSpeeds = [
  { value: 'low', label: '低速', icon: '🍃' },
  { value: 'medium', label: '中速', icon: '🍃🍃' },
  { value: 'high', label: '高速', icon: '🍃🍃🍃' },
  { value: 'auto', label: '自动', icon: '🔄' },
  { value: 'off', label: '关闭', icon: '⭕' },
]

const batteryColor = (v) => {
  if (v <= 10) return '#ef4444'
  if (v <= 20) return '#f97316'
  return '#fbbf24'
}

const toggleLight = (entity) => emit('toggle-light', entity)
const setTemp = (entity, temp) => emit('climate-action', { entity, action: 'temp', value: temp })
const setMode = (entity, mode) => emit('climate-action', { entity, action: 'mode', value: mode })
const setFanMode = (entity, fan) => emit('climate-action', { entity, action: 'fan', value: fan })
const setSwing = (entity, swing) => emit('climate-action', { entity, action: 'swing', value: swing })
</script>
