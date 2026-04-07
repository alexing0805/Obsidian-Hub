<template>
  <div class="grid-pattern min-h-screen flex flex-col text-white">

    <!-- 顶部导航栏 -->
    <header class="glass-effect border-b border-white/10 px-6 py-3 flex items-center gap-4 shrink-0 z-30">
      <!-- 返回主页按钮 -->
      <button
        class="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300"
        :class="currentTab !== 'overview' ? 'bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 ring-1 ring-cyan-500/30' : 'text-white/20 cursor-default'"
        :disabled="currentTab === 'overview'"
        @click="currentTab = 'overview'"
        title="首页"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
      </button>
 
      <div class="h-6 w-px bg-white/10 mx-1"></div>
 
      <!-- 分段导航 -->
      <nav class="flex gap-1.5 p-1 bg-white/5 rounded-xl border border-white/5">
        <button
          v-for="tab in mainTabs"
          :key="tab.id"
          class="px-4 py-1.5 rounded-lg flex items-center gap-2 text-sm font-medium transition-all duration-300 font-heading"
          :class="currentTab === tab.id ? 'bg-white/15 text-white shadow-lg' : 'text-white/40 hover:text-white/70 hover:bg-white/5'"
          @click="currentTab = tab.id"
        >
          <span class="text-base">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </nav>
 
      <div class="flex-1"></div>
 
      <!-- 系统状态区 -->
      <div class="flex items-center gap-4">
        <div class="flex flex-col items-end mr-2">
          <span class="text-[10px] uppercase tracking-tighter text-white/30 font-bold leading-none mb-1">System Status</span>
          <span class="text-xs font-heading font-semibold" :class="statusClass">{{ statusText }}</span>
        </div>
        
        <button
          class="w-10 h-10 rounded-xl glass-effect flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all"
          @click="toggleFullscreen"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
          </svg>
        </button>
      </div>
    </header>
 
    <!-- 主体区域 -->
    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧主内容区 -->
      <div class="flex-1 p-4 md:p-6 overflow-hidden bg-black/20">
        <div class="w-full h-full rounded-[2.5rem] glass-panel relative overflow-hidden shadow-2xl border-white/5 ring-1 ring-white/10">
          <transition name="fade" mode="out-in">
            <component 
              :is="currentTab === 'overview' ? FloorPlanView : (currentTab === 'settings' ? 'div' : 'div')"
              key="content"
              :ha-entities="haEntities"
              :entity-mapping="currentSettings.entity_mapping || []"
              :bg-image="currentSettings.floor_plan_image || ''"
              :weather-entity-id="currentSettings.weather_entity_id || ''"
              :ma-state="maState"
              @entity-toggle="onEntityToggle"
              @mapping-update="onMappingUpdate"
              @bg-update="onBgUpdate"
              @climate-action="onClimateAction"
              @open="activeDetail = $event"
              class="w-full h-full"
            />
          </transition>
        </div>
      </div>
 
      <!-- 右侧边栏 (宽度回缩) -->
      <aside v-if="showSidebar || currentTab === 'settings'"
        class="w-80 glass-panel flex flex-col border-l border-white/5 hidden lg:flex shadow-[-10px_0_40px_rgba(0,0,0,0.4)] h-full"
        :style="currentTab === 'settings' ? 'max-height: calc(100vh - 64px);' : ''">
        <div class="flex-1 overflow-hidden">
          <transition name="fade" mode="out-in">
            <SettingsView
              v-if="currentTab === 'settings'"
              :ha-entities="haEntities"
              :ha-connected="haConnected"
              :ma-connected="maConnected"
              :ma-state="maState"
              :system-status="systemStatus"
              :sidebar-widgets="currentSettings.sidebar_widgets || defaultSidebarWidgets"
              :weather-entity-id="currentSettings.weather_entity_id || ''"
              @save="onSettingsSave"
              @restart="onSettingsRestart"
              @toggle-sidebar="showSidebar = $event"
            />
            <SidebarWidgets
              v-else
              :ha-entities="haEntities"
              :summary="summary"
              :ma-state="maState"
              :current-time="currentTime"
              :current-date="currentDate"
              :weather-entity-id="currentSettings.weather_entity_id || ''"
              :weather-forecast="summary.weather?.forecast || []"
              :sidebar-widgets="currentSettings.sidebar_widgets || defaultSidebarWidgets"
              @open="activeDetail = $event"
              @toggle-light="onEntityToggle"
              @select-player="onSwitchPlayer"
            />
          </transition>
        </div>
      </aside>
    </main>

    <!-- 详情弹窗 -->
    <DetailOverlay
      v-if="activeDetail.type"
      :type="activeDetail.type"
      :entity-id="activeDetail.entityId"
      :ha-entities="filteredEntities"
      :ma-state="maState"
      :weather-entity-id="currentSettings.weather_entity_id || ''"
      :weather-forecast="summary.weather?.forecast || []"
      @close="activeDetail = { type: null, entityId: null }"
      @toggle-light="onEntityToggle"
      @climate-action="onClimateAction"
      @cover-action="onCoverAction"
    />

    <!-- 底部状态栏 -->
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
import MusicPlayerSelector from './components/MusicPlayerSelector.vue'
import SettingsView from './components/SettingsView.vue'
import SidebarWidgets from './components/SidebarWidgets.vue'
import DetailOverlay from './components/DetailOverlay.vue'
import FloorPlanView from './components/FloorPlanView.vue'

const mainTabs = [
  { id: 'overview', label: '总览', icon: '🏠' },
  { id: 'security', label: '安防', icon: '🔒' },
  { id: 'media', label: '影音', icon: '🎬' },
  { id: 'settings', label: '系统设置', icon: '⚙️' }
]

const currentTab = ref('overview')
const showSidebar = ref(true)
const systemStatus = ref({ ws_clients: 0 })
const currentTime = ref('')
const currentDate = ref('')
const haEntities = ref([])
const currentSettings = ref({
  sidebar_widgets: { weather: true, stats: true, lights: true, climate: true, battery: true, offline: true, music: true },
  weather_entity_id: '',
  entity_mapping: [],
})
const defaultSidebarWidgets = {
  weather: true, stats: true, lights: true, climate: true,
  battery: true, offline: true, music: true
}
const activeDetail = ref({ type: null, entityId: null })
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

const filteredEntities = computed(() => {
  const s = currentSettings.value
  const selectedLights = s.selected_light_entities || []
  const selectedClimates = s.selected_climate_entities || []
  const selectedBatteries = s.selected_battery_entities || []
  const selectedOffline = s.selected_offline_entities || []

  return haEntities.value.filter(e => {
    if (e.entity_id.startsWith('light.')) {
      return selectedLights.length === 0 || selectedLights.includes(e.entity_id)
    }
    if (e.entity_id.startsWith('climate.')) {
      return selectedClimates.length === 0 || selectedClimates.includes(e.entity_id)
    }
    if (e.entity_id.startsWith('weather.')) {
      return true
    }
    const a = e.attributes || {}
    if (a.device_class === 'battery') {
      return selectedBatteries.length === 0 || selectedBatteries.includes(e.entity_id)
    }
    // offline - if selection is empty show all, otherwise only selected
    return selectedOffline.length === 0 || selectedOffline.includes(e.entity_id)
  })
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
  currentSettings.value = { ...settings }
  console.log('Settings saved:', settings)
}

const onSettingsRestart = async () => {
  try {
    await fetch('/api/restart', { method: 'POST' })
  } catch (e) {
    console.error('Restart failed', e)
  }
}

const onClimateTemp = async ({ entity, temp }) => {
  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: 'climate',
        service: 'set_temperature',
        entity_id: entity.entity_id,
        service_data: { temperature: parseFloat(temp) }
      })
    })
  } catch (e) {
    console.error('Climate temp failed:', e)
  }
}

const onClimateMode = async ({ entity, mode }) => {
  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: 'climate',
        service: 'set_hvac_mode',
        entity_id: entity.entity_id,
        service_data: { hvac_mode: mode }
      })
    })
  } catch (e) {
    console.error('Climate mode failed:', e)
  }
}

const onClimateAction = async ({ entity, action, value }) => {
  const serviceMap = {
    temp: { service: 'set_temperature', data: { temperature: parseFloat(value) } },
    mode: { service: 'set_hvac_mode', data: { hvac_mode: value } },
    fan: { service: 'set_fan_mode', data: { fan_mode: value } },
    swing: { service: 'set_swing_mode', data: { swing_mode: value } },
  }
  const cfg = serviceMap[action]
  if (!cfg) return
  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: 'climate', service: cfg.service, entity_id: entity.entity_id, service_data: cfg.data })
    })
  } catch (e) {
    console.error('Climate action failed:', e)
  }
}

const onCoverAction = async ({ entity, action }) => {
  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: 'cover', service: action, entity_id: entity.entity_id })
    })
  } catch (e) {
    console.error('Cover action failed:', e)
  }
}

const onEntityToggle = (arg) => {
  const entity_id = typeof arg === 'string' ? arg : (arg?.entity_id || arg?.entity?.entity_id)
  const entity = typeof arg === 'object' && arg?.entity ? arg.entity : haEntities.value.find(e => e.entity_id === entity_id)
  if (!entity) return

  if (entity.entity_id.startsWith('light.')) {
    toggleLight(entity)
  } else if (entity.entity_id.startsWith('climate.')) {
    const newMode = entity.state === 'off' ? 'heat' : 'off'
    onClimateAction({ entity, action: 'mode', value: newMode })
  } else if (entity.entity_id.startsWith('switch.')) {
    const newState = entity.state === 'on' ? 'turn_off' : 'turn_on'
    fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: 'switch', service: newState, entity_id: entity.entity_id })
    })
  }
}

const onMappingUpdate = (updated) => {
  currentSettings.value = { ...currentSettings.value, entity_mapping: updated }
  saveSettingsLocal({ entity_mapping: updated })
}

const onBgUpdate = (bgData) => {
  currentSettings.value = { ...currentSettings.value, floor_plan_image: bgData }
  saveSettingsLocal({ floor_plan_image: bgData })
}

const onSwitchPlayer = async (player) => {
  try {
    await fetch('/api/ma/switch_player', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    })
    await refreshInitialState()
  } catch (e) {
    console.error('Switch player failed:', e)
  }
}


const onEntityAdd = (entity) => {
  const mapping = {
    entity_id: entity.entity_id,
    x: 0.2 + Math.random() * 0.6,
    y: 0.2 + Math.random() * 0.6,
    type: entity.entity_id.startsWith('light.') ? '灯' : (entity.entity_id.startsWith('climate.') ? '空调' : '其他'),
    label: entity.attributes?.friendly_name || entity.entity_id,
  }
  const updated = [...(currentSettings.value.entity_mapping || []), mapping]
  onMappingUpdate(updated)
}

const saveSettingsLocal = async (partial) => {
  try {
    await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...currentSettings.value, ...partial })
    })
  } catch (e) {
    console.error('Save failed:', e)
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
  // Load settings from backend first (persists entity_mapping etc)
  try {
    const r = await fetch('/api/settings')
    if (r.ok) {
      const data = await r.json()
      if (data.settings) {
        currentSettings.value = { ...currentSettings.value, ...data.settings }
      }
    }
  } catch(e) { console.error('Failed to load settings', e) }
  connectWS()
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (wsHeartbeatTimer) clearInterval(wsHeartbeatTimer)
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer)
  if (ws) ws.close()
})
</script>
