<template>
  <div class="flex flex-col h-full">

    <!-- 时钟 -->
    <div class="p-4 border-b border-white/10 shrink-0">
      <div class="text-center">
        <div class="text-3xl font-light tracking-wider">{{ currentTime }}</div>
        <div class="text-xs text-white/40 mt-1">{{ currentDate }}</div>
      </div>
    </div>

    <!-- 控件区域（可滚动） -->
    <div class="flex-1 overflow-y-auto p-4 space-y-3">

      <!-- 天气 -->
      <div v-if="widgets.weather" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('weather')">
        <div class="flex items-start justify-between mb-1">
          <div>
            <div class="text-4xl mb-1">{{ weatherEmoji }}</div>
            <div class="text-2xl font-light">{{ weatherTemperature }}</div>
            <div class="text-xs text-white/50">{{ weatherText }}</div>
          </div>
          <div class="text-right text-xs text-white/40">
            <div>{{ weatherName }}</div>
            <div class="text-white/60 mt-1">点击查看详情</div>
          </div>
        </div>
        <div class="mb-2">
          <div class="flex justify-between text-xs mb-1">
            <span class="text-white/40">空气湿度</span>
            <span class="text-white/60">{{ weatherHumidity }}</span>
          </div>
          <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div class="h-full bg-cyan-500 rounded-full" :style="{ width: weatherHumidityPercent + '%' }"></div>
          </div>
        </div>
        <div>
          <div class="flex justify-between text-xs mb-1">
            <span class="text-white/40">降水量</span>
            <span class="text-white/60">{{ weatherPrecipitation }}</span>
          </div>
          <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div class="h-full bg-white/30 rounded-full" :style="{ width: weatherPrecipitationPercent + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 统计概览 -->
      <div v-if="widgets.stats" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('stats')">
        <div class="text-xs text-white/40 mb-3">统计概览 <span class="text-white/20">点击查看详情</span></div>
        <div class="grid grid-cols-2 gap-2">
          <div class="bg-white/5 rounded-lg p-2 text-center">
            <div class="text-xs text-white/60">亮灯</div>
            <div class="text-xl font-bold text-yellow-300">{{ summary.lights_on }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-2 text-center">
            <div class="text-xs text-white/60">空调</div>
            <div class="text-xl font-bold text-blue-300">{{ summary.climate_total }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-2 text-center">
            <div class="text-xs text-white/60">低电量</div>
            <div class="text-xl font-bold text-red-300">{{ summary.low_battery_count }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-2 text-center">
            <div class="text-xs text-white/60">离线设备</div>
            <div class="text-xl font-bold text-orange-300">{{ summary.offline_count }}</div>
          </div>
        </div>
      </div>

      <!-- 灯光详情 -->
      <div v-if="widgets.lights" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('lights')">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-medium">💡 灯光</div>
          <div class="text-xs text-white/40">点击查看全部</div>
        </div>
        <div class="space-y-1">
          <div v-for="light in topLights" :key="light.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/60 truncate flex-1">{{ light.attributes?.friendly_name || light.entity_id }}</span>
            <span class="ml-2 shrink-0" :class="light.state === 'on' ? 'text-yellow-300' : 'text-white/30'">
              {{ light.state === 'on' ? '● 开' : '○ 关' }}
            </span>
          </div>
          <div v-if="!topLights.length" class="text-xs text-white/30 text-center py-1">无灯光设备</div>
        </div>
      </div>

      <!-- 空调 -->
      <div v-if="widgets.climate" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('climate')">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-medium">❄️ 空调</div>
          <div class="text-xs text-white/40">点击查看全部</div>
        </div>
        <div class="space-y-1">
          <div v-for="climate in topClimates" :key="climate.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/60 truncate flex-1">{{ climate.attributes?.friendly_name || climate.entity_id }}</span>
            <span class="ml-2 shrink-0 text-blue-300">{{ climate.attributes?.temperature || '--' }}°</span>
          </div>
          <div v-if="!topClimates.length" class="text-xs text-white/30 text-center py-1">无空调设备</div>
        </div>
      </div>

      <!-- 低电量 -->
      <div v-if="widgets.battery" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('battery')">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-medium">🔋 低电量设备</div>
          <div class="text-xs text-red-400 font-bold">{{ lowBatteryEntities.length }} 个</div>
        </div>
        <div class="space-y-1">
          <div v-for="entity in lowBatteryEntities.slice(0, 3)" :key="entity.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/60 truncate flex-1">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
            <span class="ml-2 shrink-0 text-red-400">{{ entity.state }}%</span>
          </div>
          <div v-if="!lowBatteryEntities.length" class="text-xs text-white/30 text-center py-1">无低电量设备</div>
        </div>
      </div>

      <!-- 离线设备 -->
      <div v-if="widgets.offline" class="glass-effect rounded-xl p-4 card-hover cursor-pointer"
        @click="openWidget('offline')">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm font-medium">📡 离线设备</div>
          <div class="text-xs text-orange-400 font-bold">{{ offlineEntities.length }} 个</div>
        </div>
        <div class="space-y-1">
          <div v-for="entity in offlineEntities.slice(0, 3)" :key="entity.entity_id"
            class="flex items-center justify-between text-xs">
            <span class="text-white/60 truncate flex-1">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
            <span class="ml-2 shrink-0 text-orange-400">离线</span>
          </div>
          <div v-if="!offlineEntities.length" class="text-xs text-white/30 text-center py-1">无离线设备</div>
        </div>
      </div>

      <!-- 音乐 -->
      <div v-if="widgets.music">
        <MusicAssistantPlayer :ma-state="maState" @click="openWidget('music')" class="cursor-pointer" />
      </div>

    </div>

    <!-- 详情弹窗 -->
    <div v-if="activeWidget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="activeWidget = null">
      <div class="absolute inset-0 bg-black/60" @click="activeWidget = null"></div>
      <div class="relative glass-effect rounded-2xl p-5 w-full max-w-sm max-h-[80vh] overflow-y-auto">
        <button class="absolute top-3 right-3 w-8 h-8 rounded-lg flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10"
          @click="activeWidget = null">✕</button>

        <!-- 天气详情 -->
        <div v-if="activeWidget === 'weather'">
          <h3 class="text-lg font-bold mb-4">🌤️ 天气详情</h3>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between"><span class="text-white/60">天气状态</span><span>{{ weatherText }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">温度</span><span>{{ weatherTemperature }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">湿度</span><span>{{ weatherHumidity }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">降水量</span><span>{{ weatherPrecipitation }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">实体</span><span class="font-mono text-xs">{{ weatherEntityId }}</span></div>
          </div>
        </div>

        <!-- 统计详情 -->
        <div v-if="activeWidget === 'stats'">
          <h3 class="text-lg font-bold mb-4">📊 全部统计</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-white/60">灯光总数</span><span class="font-bold">{{ summary.lights_total }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">亮灯数</span><span class="text-yellow-300 font-bold">{{ summary.lights_on }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">空调数</span><span class="text-blue-300 font-bold">{{ summary.climate_total }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">低电量</span><span class="text-red-300 font-bold">{{ summary.low_battery_count }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">离线设备</span><span class="text-orange-300 font-bold">{{ summary.offline_count }}</span></div>
            <div class="flex justify-between"><span class="text-white/60">HA 实体</span><span>{{ haEntities.length }}</span></div>
          </div>
        </div>

        <!-- 灯光详情 -->
        <div v-if="activeWidget === 'lights'">
          <h3 class="text-lg font-bold mb-4">💡 全部灯光</h3>
          <div class="space-y-1 text-sm max-h-60 overflow-y-auto">
            <div v-for="light in allLights" :key="light.entity_id"
              class="flex items-center justify-between py-1.5 border-b border-white/5">
              <span class="text-white/70 truncate flex-1">{{ light.attributes?.friendly_name || light.entity_id }}</span>
              <button class="ml-2 px-2 py-0.5 rounded text-xs border transition-colors"
                :class="light.state === 'on' ? 'border-yellow-500/50 text-yellow-300' : 'border-white/20 text-white/40'"
                @click="toggleLight(light)">
                {{ light.state === 'on' ? '● 关' : '○ 开' }}
              </button>
            </div>
            <div v-if="!allLights.length" class="text-white/30 text-center py-4">无灯光设备</div>
          </div>
        </div>

        <!-- 空调详情 -->
        <div v-if="activeWidget === 'climate'">
          <h3 class="text-lg font-bold mb-4">❄️ 全部空调</h3>
          <div class="space-y-1 text-sm max-h-60 overflow-y-auto">
            <div v-for="climate in allClimates" :key="climate.entity_id"
              class="flex items-center justify-between py-1.5 border-b border-white/5">
              <div>
                <div class="text-white/70">{{ climate.attributes?.friendly_name || climate.entity_id }}</div>
                <div class="text-xs text-white/40">{{ climate.state }} · {{ climate.attributes?.temperature || '--' }}°</div>
              </div>
            </div>
            <div v-if="!allClimates.length" class="text-white/30 text-center py-4">无空调设备</div>
          </div>
        </div>

        <!-- 低电量详情 -->
        <div v-if="activeWidget === 'battery'">
          <h3 class="text-lg font-bold mb-4">🔋 低电量设备</h3>
          <div class="space-y-1 text-sm max-h-60 overflow-y-auto">
            <div v-for="entity in lowBatteryEntities" :key="entity.entity_id"
              class="flex items-center justify-between py-1.5 border-b border-white/5">
              <span class="text-white/70 truncate flex-1">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
              <span class="ml-2 text-red-400 font-bold">{{ entity.state }}%</span>
            </div>
            <div v-if="!lowBatteryEntities.length" class="text-white/30 text-center py-4">无低电量设备</div>
          </div>
        </div>

        <!-- 离线设备详情 -->
        <div v-if="activeWidget === 'offline'">
          <h3 class="text-lg font-bold mb-4">📡 离线设备</h3>
          <div class="space-y-1 text-sm max-h-60 overflow-y-auto">
            <div v-for="entity in offlineEntities" :key="entity.entity_id"
              class="flex items-center justify-between py-1.5 border-b border-white/5">
              <span class="text-white/70 truncate flex-1">{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
              <span class="ml-2 text-orange-400">离线</span>
            </div>
            <div v-if="!offlineEntities.length" class="text-white/30 text-center py-4">无离线设备</div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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

const emit = defineEmits(['toggle-light'])

const activeWidget = ref(null)

const widgets = computed(() => ({
  weather: props.sidebarWidgets.weather !== false,
  stats: props.sidebarWidgets.stats !== false,
  lights: props.sidebarWidgets.lights !== false,
  climate: props.sidebarWidgets.climate !== false,
  battery: props.sidebarWidgets.battery !== false,
  offline: props.sidebarWidgets.offline !== false,
  music: props.sidebarWidgets.music !== false,
}))

const weatherEntity = computed(() =>
  props.haEntities.find(e => e.entity_id === props.weatherEntityId) ||
  props.haEntities.find(e => e.entity_id.startsWith('weather.')) ||
  null
)

const allLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')))
const allClimates = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('climate.')))
const topLights = computed(() => allLights.value.slice(0, 4))
const topClimates = computed(() => allClimates.value.slice(0, 4))
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
const weatherPrecipitationPercent = computed(() => Math.max(0, Math.min(100, (Number(weatherEntity.value?.attributes?.precipitation ?? 0)) * 10)))
const weatherEmoji = computed(() => {
  const s = (weatherEntity.value?.state || '').toLowerCase()
  if (s.includes('rain')) return '🌧️'
  if (s.includes('cloud')) return '☁️'
  if (s.includes('sun') || s.includes('clear')) return '☀️'
  if (s.includes('snow')) return '❄️'
  return '🌤️'
})

const openWidget = (w) => { activeWidget.value = w }
const toggleLight = (entity) => emit('toggle-light', entity)
</script>
