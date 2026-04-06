<template>
  <div class="grid-pattern min-h-screen flex text-white">
    <nav class="w-64 glass-effect flex-col z-20 hidden md:flex">
      <div class="p-4 border-b border-white/10">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
            </svg>
          </div>
          <div>
            <h1 class="font-bold text-sm">Obsidian Hub</h1>
            <span class="text-xs status-badge" :class="statusClass">{{ statusText }}</span>
          </div>
        </div>
      </div>

      <div class="flex-1 py-4 px-3 space-y-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="nav-item w-full text-left px-4 py-3 rounded-lg border border-transparent text-sm font-medium flex items-center gap-3"
          :class="{ 'active': currentTab === tab.id, 'text-white/60': currentTab !== tab.id }"
          @click="currentTab = tab.id"
        >
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="p-4 border-t border-white/10">
        <button
          class="w-full px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          @click="toggleFullscreen"
        >
          全屏显示
        </button>
      </div>
    </nav>

    <main class="flex-1 flex overflow-hidden pb-14 md:pb-10">
      <div class="flex-1 p-4 md:p-6 overflow-hidden">
        <div class="w-full h-full rounded-2xl glass-effect relative overflow-hidden">
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
                  @click="toggleLight(light)"
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
              <span v-else>暂无可控灯光</span>
            </div>
          </div>
        </div>
      </div>

      <aside v-if="showSidebar || currentTab === 'settings'" class="w-[340px] glass-effect flex-col border-l border-white/10 hidden lg:flex overflow-y-auto">
        <template v-if="currentTab === 'settings'">
          <SettingsView
            :ha-entities="haEntities"
            :ha-connected="haConnected"
            :ma-connected="maConnected"
            :ma-state="maState"
            :system-status="systemStatus"
            @save="onSettingsSave"
            @restart="onSettingsRestart"
            @toggle-sidebar="showSidebar = $event"
          />
        </template>
        <template v-else>
          <div class="p-4 border-b border-white/10">
            <div class="text-center mb-4">
              <div class="text-3xl font-light tracking-wider">{{ currentTime }}</div>
              <div class="text-xs text-white/40 mt-1">{{ currentDate }}</div>
            </div>

            <div class="glass-effect rounded-xl p-4 card-hover">
              <div class="flex items-start justify-between mb-3">
                <div>
                  <div class="text-4xl mb-1">{{ weatherEmoji }}</div>
                  <div class="text-2xl font-light">{{ weatherTemperature }}</div>
                  <div class="text-xs text-white/50">{{ weatherText }}</div>
                </div>
                <div class="text-right text-xs text-white/40">
                  <div>{{ weatherName }}</div>
                  <div class="text-white/60 mt-1">今日天气</div>
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
          </div>

          <div class="p-4 border-b border-white/10">
            <div class="grid grid-cols-2 gap-2">
              <div class="glass-effect rounded-xl p-3 text-center card-hover">
                <div class="text-xs text-white/60">亮灯</div>
                <div class="text-xl font-bold text-yellow-300">{{ summary.lights_on }}</div>
              </div>
              <div class="glass-effect rounded-xl p-3 text-center card-hover">
                <div class="text-xs text-white/60">空调</div>
                <div class="text-xl font-bold text-blue-300">{{ summary.climate_total }}</div>
              </div>
              <div class="glass-effect rounded-xl p-3 text-center card-hover">
                <div class="text-xs text-white/60">低电量</div>
                <div class="text-xl font-bold text-red-300">{{ summary.low_battery_count }}</div>
              </div>
              <div class="glass-effect rounded-xl p-3 text-center card-hover">
                <div class="text-xs text-white/60">离线设备</div>
                <div class="text-xl font-bold text-orange-300">{{ summary.offline_count }}</div>
              </div>
            </div>
          </div>

          <MusicAssistantPlayer :ma-state="maState" />
        </template>
      </aside>
    </main>

    <div class="fixed bottom-0 left-0 right-0 glass-effect border-t border-white/10 py-2 px-4 md:px-6">
      <div class="flex items-center justify-between text-xs text-white/40 gap-4">
        <div class="flex items-center gap-4 md:gap-10 overflow-x-auto">
          <span>灯光总数: {{ summary.lights_total }}</span>
          <span>HA 实体: {{ haEntities.length }}</span>
          <span>MA 队列: {{ maState.queues?.length || 0 }}</span>
          <span>更新时间: {{ currentTime }}</span>
        </div>
        <div class="text-white/60 whitespace-nowrap">{{ statusText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import MusicAssistantPlayer from './components/MusicAssistantPlayer.vue'
import SettingsView from './components/SettingsView.vue'

const tabs = [
  { id: 'overview', label: '总览' },
  { id: 'security', label: '安防' },
  { id: 'media', label: '影音' },
  { id: 'settings', label: '系统设置' }
]

const currentTab = ref('overview')
const showSidebar = ref(true)
const systemStatus = ref({ ws_clients: 0 })
const currentTime = ref('')
const currentDate = ref('')
const haEntities = ref([])
const summary = ref({
  lights_total: 0,
  lights_on: 0,
  climate_total: 0,
  low_battery_count: 0,
  offline_count: 0,
  temperature: null,
  humidity: null,
  weather: null
})
const maState = ref({
  connected: false,
  queues: [],
  players: [],
  active_queue_id: null,
  active_player_id: null,
  queue_player_map: {},
  ma_base_url: ''
})

const wsConnected = ref(false)
let ws = null
let wsReconnectTimer = null
let wsHeartbeatTimer = null
let clockInterval = null

const lightPositions = [
  [140, 130],
  [240, 170],
  [560, 130],
  [660, 170],
  [120, 350],
  [280, 430],
  [430, 390],
  [620, 350]
]

const floorLights = computed(() => {
  return haEntities.value
    .filter((entity) => entity.entity_id?.startsWith('light.'))
    .slice(0, lightPositions.length)
})

const haConnected = computed(() => haEntities.value.length > 0)
const maConnected = computed(() => !!maState.value.connected)

const statusText = computed(() => {
  if (haConnected.value && maConnected.value) return 'HA + MA ONLINE'
  if (haConnected.value) return 'HA ONLINE / MA OFFLINE'
  if (maConnected.value) return 'HA OFFLINE / MA ONLINE'
  return 'DISCONNECTED'
})

const onSettingsSave = (settings) => {
  console.log('Settings saved:', settings)
}

const onSettingsRestart = async () => {
  try {
    await fetch('/api/restart', { method: 'POST' })
  } catch (e) {
    console.error('Restart failed', e)
  }
}

const statusClass = computed(() => {
  if (haConnected.value && maConnected.value) return 'text-emerald-400'
  if (haConnected.value || maConnected.value) return 'text-yellow-300'
  return 'text-red-400'
})

const displayTemperature = computed(() => {
  const value = summary.value.temperature
  return value === null || value === undefined ? '--' : `${Number(value).toFixed(1)}°C`
})

const displayHumidity = computed(() => {
  const value = summary.value.humidity
  return value === null || value === undefined ? '--' : `${Math.round(Number(value))}%`
})

const weather = computed(() => summary.value.weather || null)

const weatherText = computed(() => weather.value?.state || '未知')
const weatherName = computed(() => weather.value?.friendly_name || '天气')
const weatherTemperature = computed(() => {
  const value = weather.value?.temperature
  return value === null || value === undefined ? '--' : `${Number(value).toFixed(1)}°`
})
const weatherHumidity = computed(() => {
  const value = weather.value?.humidity
  return value === null || value === undefined ? '--' : `${Math.round(Number(value))}%`
})
const weatherPrecipitation = computed(() => {
  const value = weather.value?.precipitation
  return value === null || value === undefined ? '0 mm' : `${Number(value).toFixed(1)} mm`
})
const weatherHumidityPercent = computed(() => {
  const value = Number(weather.value?.humidity ?? 0)
  return Math.max(0, Math.min(100, value))
})
const weatherPrecipitationPercent = computed(() => {
  const value = Number(weather.value?.precipitation ?? 0)
  return Math.max(0, Math.min(100, value * 10))
})

const weatherEmoji = computed(() => {
  const state = (weather.value?.state || '').toLowerCase()
  if (state.includes('rain')) return '🌧️'
  if (state.includes('cloud')) return '☁️'
  if (state.includes('sun') || state.includes('clear')) return '☀️'
  if (state.includes('snow')) return '❄️'
  return '🌤️'
})

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const fetchHAState = async () => {
  const response = await fetch('/api/ha/entities')
  if (!response.ok) throw new Error(`HA request failed: ${response.status}`)
  const data = await response.json()
  haEntities.value = data.entities || []
  if (data.summary) summary.value = data.summary
}

const fetchMAState = async () => {
  const response = await fetch('/api/ma/state')
  if (!response.ok) throw new Error(`MA request failed: ${response.status}`)
  const data = await response.json()
  maState.value = data.state || maState.value
}

const refreshInitialState = async () => {
  try {
    await Promise.all([fetchHAState(), fetchMAState()])
  } catch (error) {
    console.error('Failed to refresh initial state', error)
  }
}

const toggleLight = async (entity) => {
  if (!entity?.entity_id) return

  const index = haEntities.value.findIndex((item) => item.entity_id === entity.entity_id)
  if (index === -1) return

  const previousState = haEntities.value[index].state
  const nextState = previousState === 'on' ? 'off' : 'on'
  haEntities.value[index] = {
    ...haEntities.value[index],
    state: nextState
  }

  if (summary.value.lights_on !== undefined) {
    summary.value = {
      ...summary.value,
      lights_on: Math.max(0, summary.value.lights_on + (nextState === 'on' ? 1 : -1))
    }
  }

  try {
    const response = await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: 'light',
        service: nextState === 'on' ? 'turn_on' : 'turn_off',
        entity_id: entity.entity_id
      })
    })

    if (!response.ok) throw new Error(`HA service failed: ${response.status}`)
  } catch (error) {
    haEntities.value[index] = {
      ...haEntities.value[index],
      state: previousState
    }
    console.error('Failed to toggle light', error)
    await fetchHAState()
  }
}

const connectWS = () => {
  if (ws) {
    ws.close()
    ws = null
  }

  const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${wsProtocol}://${window.location.host}/api/ws`)

  ws.onopen = () => {
    wsConnected.value = true
    if (wsHeartbeatTimer) clearInterval(wsHeartbeatTimer)
    wsHeartbeatTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 20000)
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'init') {
        if (Array.isArray(data.ha_entities)) {
          haEntities.value = data.ha_entities
        }
        if (data.ha_summary) {
          summary.value = data.ha_summary
        }
        if (data.ma_state) {
          maState.value = data.ma_state
        }
      }
      if (data.type === 'ha_state') {
        if (Array.isArray(data.entities)) {
          haEntities.value = data.entities
        }
        if (data.summary) {
          summary.value = data.summary
        }
      }
      if (data.type === 'ma_state' && data.state) {
        maState.value = data.state
      }
    } catch (error) {
      console.error('WS parse error', error)
    }
  }

  ws.onclose = () => {
    wsConnected.value = false
    if (wsHeartbeatTimer) {
      clearInterval(wsHeartbeatTimer)
      wsHeartbeatTimer = null
    }
    if (wsReconnectTimer) clearTimeout(wsReconnectTimer)
    wsReconnectTimer = setTimeout(connectWS, 4000)
  }

  ws.onerror = () => {
    if (ws) ws.close()
  }
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

onMounted(async () => {
  updateClock()
  clockInterval = setInterval(updateClock, 1000)
  await refreshInitialState()
  connectWS()
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (wsHeartbeatTimer) clearInterval(wsHeartbeatTimer)
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer)
  if (ws) ws.close()
})
</script>
