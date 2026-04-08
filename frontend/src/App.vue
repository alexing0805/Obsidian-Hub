<template>
  <div class="grid-pattern min-h-screen flex flex-col text-white">
    <header class="glass-effect border-b border-white/10 px-4 py-1.5 flex items-center gap-4 shrink-0 z-30">
      <nav class="flex gap-1 p-1 bg-white/5 rounded-xl border border-white/5">
        <button
          v-for="tab in mainTabs"
          :key="tab.id"
          class="px-3.5 py-1.5 rounded-lg flex items-center gap-2 text-sm font-medium transition-all duration-300 font-heading min-w-[88px] justify-center"
          :class="currentTab === tab.id ? 'bg-white/15 text-white shadow-lg ring-1 ring-white/20' : 'text-white/40 hover:text-white/70 hover:bg-white/5'"
          @click="currentTab = tab.id"
        >
          <span class="text-base">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </nav>

      <div class="flex-1"></div>

      <div class="flex items-center gap-4">
        <div class="flex flex-col items-end mr-1">
          <span class="text-[0.65rem] uppercase tracking-wider text-white/30 font-bold leading-none mb-0.5">System Status</span>
          <span class="text-xs font-heading font-semibold" :class="statusClass">{{ statusText }}</span>
        </div>

        <button
          class="w-9 h-9 rounded-xl glass-effect flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all border border-white/5"
          @click="toggleFullscreen"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
          </svg>
        </button>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      <div class="flex-1 p-1 overflow-hidden bg-black/20">
        <div class="w-full h-full rounded-[2.5rem] glass-panel relative overflow-hidden shadow-2xl border-white/5 ring-1 ring-white/10">
          <transition name="fade" mode="out-in">
            <FloorPlanView
              v-if="currentTab === 'overview'"
              key="overview"
              :ha-entities="haEntities"
              :entity-mapping="currentSettings.entity_mapping || []"
              :bg-image="currentSettings.floor_plan_image || ''"
              :kiosk-mode="resolvedKioskMode"
              @entity-toggle="onEntityToggle"
              @mapping-update="onMappingUpdate"
              @bg-update="onBgUpdate"
              @open="activeDetail = $event"
              class="w-full h-full"
            />
            <div v-else key="settings-placeholder" class="w-full h-full"></div>
          </transition>
        </div>
      </div>

      <aside
        v-if="showSidebar || currentTab === 'settings'"
        class="w-72 glass-panel flex flex-col border-l border-white/5 shadow-[-10px_0_40px_rgba(0,0,0,0.4)] h-full"
        :style="currentTab === 'settings' ? 'max-height: calc(100vh - 64px);' : ''"
      >
        <transition name="fade" mode="out-in">
          <SettingsView
            v-if="currentTab === 'settings'"
            :settings="currentSettings"
            :ha-entities="haEntities"
            :ha-connected="haConnected"
            :ma-connected="maConnected"
            :ma-state="maState"
            :system-status="systemStatus"
            @save="onSettingsSave"
          />
          <SidebarWidgets
            v-else
            :ha-entities="haEntities"
            :summary="dashboardSummary"
            :ma-state="maState"
            :kiosk-mode="resolvedKioskMode"
            :current-time="currentTime"
            :current-date="currentDate"
            :weather-entity-id="currentSettings.weather_entity_id || ''"
            :sidebar-widgets="currentSettings.sidebar_widgets || defaultSidebarWidgets"
            :selected-light-entities="currentSettings.selected_light_entities || []"
            :selected-climate-entities="currentSettings.selected_climate_entities || []"
            :selected-cover-entities="currentSettings.selected_cover_entities || []"
            :selected-battery-entities="currentSettings.selected_battery_entities || []"
            :selected-offline-entities="currentSettings.selected_offline_entities || []"
            class="flex-1 min-h-0"
            @open="activeDetail = $event"
            @select-player="onSwitchPlayer"
          />
        </transition>
      </aside>
    </main>

    <DetailOverlay
      v-if="activeDetail.type"
      :type="activeDetail.type"
      :entity-id="activeDetail.entityId"
      :ha-entities="haEntities"
      :ma-state="maState"
      :kiosk-mode="resolvedKioskMode"
      :summary="dashboardSummary"
      :weather-entity-id="currentSettings.weather_entity_id || ''"
      :selected-light-entities="currentSettings.selected_light_entities || []"
      :selected-climate-entities="currentSettings.selected_climate_entities || []"
      :selected-cover-entities="currentSettings.selected_cover_entities || []"
      :selected-battery-entities="currentSettings.selected_battery_entities || []"
      :selected-offline-entities="currentSettings.selected_offline_entities || []"
      @close="activeDetail = { type: null, entityId: null }"
      @toggle-light="onEntityToggle"
      @climate-action="onClimateAction"
      @cover-action="onCoverAction"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import DetailOverlay from './components/DetailOverlay.vue'
import FloorPlanView from './components/FloorPlanView.vue'
import SettingsView from './components/SettingsView.vue'
import SidebarWidgets from './components/SidebarWidgets.vue'

const mainTabs = [
  { id: 'overview', label: '首页', icon: '🏠' },
  { id: 'settings', label: '系统设置', icon: '⚙️' }
]

const defaultSidebarWidgets = {
  weather: true,
  stats: true,
  lights: true,
  climate: true,
  battery: true,
  offline: true,
  music: true
}

const defaultSettings = () => ({
  ha_url: '',
  ha_token: '',
  ma_url: '',
  ma_token: '',
  ha_refresh_interval: 15,
  ma_refresh_interval: 5,
  temperature_entity: '',
  humidity_entity: '',
  entity_mapping: [],
  show_sidebar: true,
  clock_24h: true,
  show_seconds: false,
  kiosk_mode: true,
  sidebar_widgets: { ...defaultSidebarWidgets },
  weather_entity_id: '',
  selected_light_entities: [],
  selected_climate_entities: [],
  selected_cover_entities: [],
  selected_battery_entities: [],
  selected_offline_entities: [],
  floor_plan_image: '',
  ha_token_masked: '',
  ma_token_masked: ''
})

const currentTab = ref('overview')
const showSidebar = ref(true)
const systemStatus = ref({ ws_clients: 0 })
const currentTime = ref('')
const currentDate = ref('')
const haEntities = ref([])
const currentSettings = ref(defaultSettings())
const activeDetail = ref({ type: null, entityId: null })
const summary = ref({
  lights_total: 0,
  lights_on: 0,
  climate_total: 0,
  climate_active: 0,
  cover_total: 0,
  cover_open: 0,
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
let clockInterval = null

const haConnected = computed(() => haEntities.value.length > 0)
const maConnected = computed(() => !!maState.value.connected)
const autoDetectedKioskMode = computed(() => {
  if (typeof navigator === 'undefined') return false
  const userAgent = navigator.userAgent.toLowerCase()
  return userAgent.includes('fully') || userAgent.includes('android')
})
const resolvedKioskMode = computed(() => currentSettings.value.kiosk_mode ?? autoDetectedKioskMode.value)

const filterBySelected = (entities, selectedIds) => {
  if (!Array.isArray(selectedIds) || selectedIds.length === 0) return entities
  const selected = new Set(selectedIds)
  return entities.filter((entity) => selected.has(entity.entity_id))
}

const dashboardSummary = computed(() => {
  const lights = filterBySelected(
    haEntities.value.filter((entity) => entity.entity_id.startsWith('light.')),
    currentSettings.value.selected_light_entities
  )
  const climates = filterBySelected(
    haEntities.value.filter((entity) => entity.entity_id.startsWith('climate.')),
    currentSettings.value.selected_climate_entities
  )
  const covers = filterBySelected(
    haEntities.value.filter((entity) => entity.entity_id.startsWith('cover.')),
    currentSettings.value.selected_cover_entities
  )
  const batteryScope = filterBySelected(
    haEntities.value.filter((entity) => entity.attributes?.device_class === 'battery'),
    currentSettings.value.selected_battery_entities
  )
  const offlineScope = filterBySelected(
    haEntities.value,
    currentSettings.value.selected_offline_entities
  )

  return {
    ...summary.value,
    lights_total: lights.length,
    lights_on: lights.filter((entity) => entity.state === 'on').length,
    climate_total: climates.length,
    climate_active: climates.filter((entity) => String(entity.state).toLowerCase() !== 'off').length,
    cover_total: covers.length,
    cover_open: covers.filter((entity) => String(entity.state).toLowerCase() === 'open').length,
    low_battery_count: batteryScope.filter((entity) => {
      const value = parseFloat(entity.state)
      return !Number.isNaN(value) && value <= 20
    }).length,
    offline_count: offlineScope.filter((entity) =>
      ['unknown', 'unavailable', 'none', ''].includes(String(entity.state).toLowerCase())
    ).length
  }
})

const statusText = computed(() => {
  if (haConnected.value && maConnected.value) return 'HA + MA ONLINE'
  if (haConnected.value) return 'HA ONLINE / MA OFFLINE'
  if (maConnected.value) return 'HA OFFLINE / MA ONLINE'
  if (wsConnected.value) return 'BACKEND ONLINE'
  return 'DISCONNECTED'
})

const statusClass = computed(() => {
  if (haConnected.value && maConnected.value) return 'text-emerald-400'
  if (haConnected.value || maConnected.value || wsConnected.value) return 'text-yellow-300'
  return 'text-red-400'
})

watch(
  () => currentSettings.value.show_sidebar,
  (value) => {
    showSidebar.value = value !== false
  },
  { immediate: true }
)

watch(
  resolvedKioskMode,
  (enabled) => {
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('kiosk-mode', !!enabled)
    }
  },
  { immediate: true }
)

const mergeSettings = (settings = {}) => {
  currentSettings.value = {
    ...defaultSettings(),
    ...currentSettings.value,
    ...settings,
    sidebar_widgets: {
      ...defaultSidebarWidgets,
      ...(settings.sidebar_widgets || currentSettings.value.sidebar_widgets || {})
    }
  }
}

const onSettingsSave = (settings) => {
  mergeSettings(settings)
}

const onClimateAction = async ({ entity, action, value }) => {
  const serviceMap = {
    temp: { service: 'set_temperature', data: { temperature: parseFloat(value) } },
    mode: { service: 'set_hvac_mode', data: { hvac_mode: value } },
    fan: { service: 'set_fan_mode', data: { fan_mode: value } },
    swing: { service: 'set_swing_mode', data: { swing_mode: value } }
  }
  const cfg = serviceMap[action]
  if (!cfg || !entity?.entity_id) return

  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: 'climate',
        service: cfg.service,
        entity_id: entity.entity_id,
        service_data: cfg.data
      })
    })
  } catch (error) {
    console.error('Climate action failed:', error)
  }
}

const onCoverAction = async (payload) => {
  if (!payload) return

  const haPayload = payload.service && payload.entityId
    ? {
        domain: 'cover',
        service: payload.service,
        entity_id: payload.entityId,
        service_data: payload.data || {}
      }
    : {
        domain: 'cover',
        service: payload.action,
        entity_id: payload.entity?.entity_id,
        service_data: payload.value !== undefined ? { position: parseInt(payload.value, 10) } : undefined
      }

  if (!haPayload.entity_id || !haPayload.service) return

  try {
    await fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(haPayload)
    })
  } catch (error) {
    console.error('Cover action failed:', error)
  }
}

const onEntityToggle = (arg) => {
  const entityId = typeof arg === 'string' ? arg : (arg?.entity_id || arg?.entity?.entity_id)
  const entity = typeof arg === 'object' && arg?.entity
    ? arg.entity
    : haEntities.value.find((item) => item.entity_id === entityId)

  if (!entity?.entity_id) return

  if (entity.entity_id.startsWith('light.')) {
    toggleLight(entity)
    return
  }

  if (entity.entity_id.startsWith('climate.')) {
    const nextMode = entity.state === 'off' ? 'heat' : 'off'
    onClimateAction({ entity, action: 'mode', value: nextMode })
    return
  }

  if (entity.entity_id.startsWith('switch.')) {
    const service = entity.state === 'on' ? 'turn_off' : 'turn_on'
    fetch('/api/ha/service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: 'switch', service, entity_id: entity.entity_id })
    }).catch((error) => {
      console.error('Switch action failed:', error)
    })
  }
}

const saveSettingsLocal = async (partial) => {
  const nextSettings = {
    ...currentSettings.value,
    ...partial,
    sidebar_widgets: {
      ...defaultSidebarWidgets,
      ...(currentSettings.value.sidebar_widgets || {}),
      ...(partial.sidebar_widgets || {})
    }
  }

  mergeSettings(nextSettings)

  try {
    const response = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nextSettings)
    })

    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`)
    }

    const data = await response.json()
    mergeSettings(data.settings || nextSettings)
  } catch (error) {
    console.error('Save failed:', error)
  }
}

const onMappingUpdate = (updated) => {
  saveSettingsLocal({ entity_mapping: updated })
}

const onBgUpdate = (bgData) => {
  saveSettingsLocal({ floor_plan_image: bgData })
}

const onSwitchPlayer = async (player) => {
  if (!player?.player_id) return

  try {
    await fetch('/api/ma/switch_player', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    })
  } catch (error) {
    console.error('Switch player failed:', error)
  }
}

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour12: !currentSettings.value.clock_24h,
    second: currentSettings.value.show_seconds ? '2-digit' : undefined
  })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const restartClock = () => {
  if (clockInterval) clearInterval(clockInterval)
  updateClock()
  const interval = currentSettings.value.show_seconds ? 1000 : 30000
  clockInterval = setInterval(updateClock, interval)
}

const fetchSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    if (!response.ok) throw new Error(`Settings request failed: ${response.status}`)
    const data = await response.json()
    mergeSettings(data.settings)
  } catch (error) {
    console.error('Failed to load settings', error)
  }
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

const fetchStatus = async () => {
  try {
    const response = await fetch('/api/status')
    if (!response.ok) return
    const data = await response.json()
    systemStatus.value = data.status || systemStatus.value
  } catch (error) {
    console.error('Failed to load status', error)
  }
}

const refreshInitialState = async () => {
  try {
    await Promise.all([fetchSettings(), fetchHAState(), fetchMAState(), fetchStatus()])
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

  haEntities.value[index] = { ...haEntities.value[index], state: nextState }
  summary.value = {
    ...summary.value,
    lights_on: Math.max(0, (summary.value.lights_on || 0) + (nextState === 'on' ? 1 : -1))
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
    haEntities.value[index] = { ...haEntities.value[index], state: previousState }
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
        return
      }

      if (data.type === 'ha_state') {
        if (Array.isArray(data.entities)) {
          haEntities.value = data.entities
        }
        if (data.summary) {
          summary.value = data.summary
        }
        return
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
  await refreshInitialState()
  restartClock()
  connectWS()
})

watch(
  () => [currentSettings.value.clock_24h, currentSettings.value.show_seconds],
  () => {
    restartClock()
  }
)

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer)
  if (ws) ws.close()
})
</script>
