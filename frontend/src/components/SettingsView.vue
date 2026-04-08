<template>
  <div class="settings-view flex flex-col min-h-0 h-full">
    <div class="shrink-0 px-4 pt-4 pb-2 flex items-center gap-1 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="px-3 py-1.5 text-xs rounded-lg transition-colors"
        :class="currentTab === tab.id ? 'bg-white/15 text-white' : 'text-white/45 hover:text-white/70'"
        @click="currentTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-5 min-h-0">
      <template v-if="currentTab === 'connection'">
        <section class="glass-effect rounded-xl p-4 space-y-4">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-blue-600/30 flex items-center justify-center text-xs">HA</div>
            <div class="font-semibold text-sm">Home Assistant</div>
            <div class="ml-auto">
              <span class="text-xs px-2 py-1 rounded" :class="haConnectedClass">{{ haConnectedText }}</span>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">HA 地址</label>
              <input v-model.trim="localSettings.ha_url" type="text" placeholder="http://192.168.1.100:8123" class="settings-input w-full" @input="markDirty" />
            </div>

            <div>
              <label class="block text-xs text-white/60 mb-1">HA Token</label>
              <input
                v-model.trim="localSettings.ha_token"
                type="password"
                :placeholder="props.settings.ha_token_masked || '留空则保留当前 Token'"
                class="settings-input w-full"
                @input="markDirty"
              />
              <div v-if="props.settings.ha_token_masked" class="text-[11px] text-white/30 mt-1">
                当前已保存：{{ props.settings.ha_token_masked }}
              </div>
            </div>

            <div class="flex items-center gap-3">
              <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
              <input v-model.number="localSettings.ha_refresh_interval" type="number" min="5" max="300" class="settings-input w-24" @input="markDirty" />
              <span class="text-xs text-white/40">秒</span>
            </div>
          </div>
        </section>

        <section class="glass-effect rounded-xl p-4 space-y-4">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-cyan-600/30 flex items-center justify-center text-xs">MA</div>
            <div class="font-semibold text-sm">Music Assistant</div>
            <div class="ml-auto">
              <span class="text-xs px-2 py-1 rounded" :class="maConnectedClass">{{ maConnectedText }}</span>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">MA WebSocket 地址</label>
              <input v-model.trim="localSettings.ma_url" type="text" placeholder="ws://192.168.1.100:8095/ws" class="settings-input w-full" @input="markDirty" />
            </div>

            <div>
              <label class="block text-xs text-white/60 mb-1">MA Token</label>
              <input
                v-model.trim="localSettings.ma_token"
                type="password"
                :placeholder="props.settings.ma_token_masked || '留空则保留当前 Token'"
                class="settings-input w-full"
                @input="markDirty"
              />
              <div v-if="props.settings.ma_token_masked" class="text-[11px] text-white/30 mt-1">
                当前已保存：{{ props.settings.ma_token_masked }}
              </div>
            </div>

            <div class="flex items-center gap-3">
              <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
              <input v-model.number="localSettings.ma_refresh_interval" type="number" min="2" max="60" class="settings-input w-24" @input="markDirty" />
              <span class="text-xs text-white/40">秒</span>
            </div>
          </div>
        </section>
      </template>

      <template v-else-if="currentTab === 'display'">
        <section class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">侧栏组件</div>
          <div class="space-y-2">
            <label v-for="(label, key) in widgetLabels" :key="key" class="flex items-center gap-3 cursor-pointer group">
              <input v-model="localSettings.sidebar_widgets[key]" type="checkbox" class="w-4 h-4 rounded accent-emerald-500" @change="markDirty" />
              <span class="text-sm text-white/70 group-hover:text-white transition-colors">{{ label }}</span>
            </label>
          </div>
        </section>

        <section class="glass-effect rounded-xl p-4 space-y-4">
          <div class="text-sm font-medium">显示与壁挂</div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">天气实体</label>
              <select v-model="localSettings.weather_entity_id" class="settings-input w-full" @change="markDirty">
                <option value="">自动选择</option>
                <option v-for="entity in weatherEntities" :key="entity.entity_id" :value="entity.entity_id">
                  {{ entity.attributes?.friendly_name || entity.entity_id }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-white/60 mb-1">时钟格式</label>
              <select v-model="clockFormatValue" class="settings-input w-full" @change="markDirty">
                <option value="24">24 小时制</option>
                <option value="12">12 小时制</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">温度来源</label>
              <select v-model="localSettings.temperature_entity" class="settings-input w-full" @change="markDirty">
                <option value="">自动选择</option>
                <option v-for="entity in temperatureEntities" :key="entity.entity_id" :value="entity.entity_id">
                  {{ entity.attributes?.friendly_name || entity.entity_id }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-white/60 mb-1">湿度来源</label>
              <select v-model="localSettings.humidity_entity" class="settings-input w-full" @change="markDirty">
                <option value="">自动选择</option>
                <option v-for="entity in humidityEntities" :key="entity.entity_id" :value="entity.entity_id">
                  {{ entity.attributes?.friendly_name || entity.entity_id }}
                </option>
              </select>
            </div>
          </div>

          <div class="text-xs text-white/35">
            温湿度会显示在主页右侧的室内温度和湿度卡片中。
          </div>

          <label class="flex items-center justify-between gap-3 cursor-pointer">
            <span class="text-sm text-white/70">显示右侧边栏</span>
            <input v-model="localSettings.show_sidebar" type="checkbox" class="w-4 h-4 rounded accent-emerald-500" @change="markDirty" />
          </label>
          <label class="flex items-center justify-between gap-3 cursor-pointer">
            <span class="text-sm text-white/70">启用 Fully Kiosk 优化</span>
            <input v-model="localSettings.kiosk_mode" type="checkbox" class="w-4 h-4 rounded accent-emerald-500" @change="markDirty" />
          </label>
          <label class="flex items-center justify-between gap-3 cursor-pointer">
            <span class="text-sm text-white/70">时钟显示秒</span>
            <input v-model="localSettings.show_seconds" type="checkbox" class="w-4 h-4 rounded accent-cyan-500" @change="markDirty" />
          </label>
        </section>

        <section class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">主页快捷与统计筛选</div>
          <div class="text-xs text-white/40 mb-3">这里选中的实体，会同时影响主页按钮、统计数字和点击后的弹层内容。留空表示该类默认显示全部。</div>

          <div class="space-y-5">
            <div>
              <div class="flex items-center justify-between mb-2">
                <div class="text-xs uppercase tracking-[0.2em] text-white/30">灯光快捷</div>
                <button class="text-[11px] text-white/45 hover:text-white" @click="toggleAll('light')">{{ allLightsSelected ? '清空' : '全选' }}</button>
              </div>
              <div class="selection-list">
                <label v-for="entity in allLights" :key="entity.entity_id" class="selection-item">
                  <input v-model="localSettings.selected_light_entities" type="checkbox" :value="entity.entity_id" class="w-3.5 h-3.5 rounded accent-yellow-400" @change="markDirty" />
                  <span>{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                </label>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <div class="text-xs uppercase tracking-[0.2em] text-white/30">空调快捷</div>
                <button class="text-[11px] text-white/45 hover:text-white" @click="toggleAll('climate')">{{ allClimatesSelected ? '清空' : '全选' }}</button>
              </div>
              <div class="selection-list">
                <label v-for="entity in allClimates" :key="entity.entity_id" class="selection-item">
                  <input v-model="localSettings.selected_climate_entities" type="checkbox" :value="entity.entity_id" class="w-3.5 h-3.5 rounded accent-blue-400" @change="markDirty" />
                  <span>{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                </label>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <div class="text-xs uppercase tracking-[0.2em] text-white/30">窗帘快捷</div>
                <button class="text-[11px] text-white/45 hover:text-white" @click="toggleAll('cover')">{{ allCoversSelected ? '清空' : '全选' }}</button>
              </div>
              <div class="selection-list">
                <label v-for="entity in allCovers" :key="entity.entity_id" class="selection-item">
                  <input v-model="localSettings.selected_cover_entities" type="checkbox" :value="entity.entity_id" class="w-3.5 h-3.5 rounded accent-sky-400" @change="markDirty" />
                  <span>{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                </label>
              </div>
            </div>

            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-white/30 mb-2">低电量统计</div>
              <div class="selection-list">
                <label v-for="entity in batteryEntities" :key="entity.entity_id" class="selection-item">
                  <input v-model="localSettings.selected_battery_entities" type="checkbox" :value="entity.entity_id" class="w-3.5 h-3.5 rounded accent-red-400" @change="markDirty" />
                  <span>{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                </label>
              </div>
            </div>

            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-white/30 mb-2">离线统计</div>
              <div class="selection-list">
                <label v-for="entity in allEntities" :key="entity.entity_id" class="selection-item">
                  <input v-model="localSettings.selected_offline_entities" type="checkbox" :value="entity.entity_id" class="w-3.5 h-3.5 rounded accent-orange-400" @change="markDirty" />
                  <span>{{ entity.attributes?.friendly_name || entity.entity_id }}</span>
                </label>
              </div>
            </div>
          </div>
        </section>
      </template>

      <template v-else-if="currentTab === 'floorplan'">
        <section class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-2">户型图实体映射</div>
          <div class="text-xs text-white/40 mb-3">布局在主页编辑模式里拖动，这里负责查看、删除以及灯光图标样式选择。</div>
          <div class="space-y-4">
            <div v-for="(mappings, type) in groupedMappings" :key="type" class="space-y-2">
              <div class="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] ml-1">{{ type }}</div>
              <div
                v-for="mapping in mappings"
                :key="mapping.entity_id"
                class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/5"
              >
                <span>{{ entityTypeIcon(mapping.type) }}</span>
                <div class="flex-1 min-w-0">
                  <div class="text-xs truncate text-white/70">{{ mapping.label || mapping.entity_id }}</div>
                  <div class="text-[10px] font-bold tabular-nums text-white/30">
                    {{ Math.round((mapping.x || 0.5) * 100) }}%, {{ Math.round((mapping.y || 0.5) * 100) }}%
                  </div>
                  <div v-if="mapping.type === 'light'" class="mt-2">
                    <select
                      :value="mapping.icon_variant || 'bulb'"
                      class="settings-input w-full text-xs"
                      @change="updateMappingIcon(mapping.entity_id, $event.target.value)"
                    >
                      <option v-for="option in lightIconOptions" :key="option.value" :value="option.value">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                </div>
                <button
                  class="text-[10px] font-bold text-red-400 hover:text-white hover:bg-red-500/40 px-2 py-1 rounded border border-red-500/20 transition-all"
                  @click="removeMapping(mapping.entity_id)"
                >
                  删除
                </button>
              </div>
            </div>
            <div v-if="!localSettings.entity_mapping?.length" class="text-xs text-white/30 text-center py-4 bg-white/5 rounded-xl border border-dashed border-white/10">
              当前还没有户型图映射。
            </div>
          </div>
        </section>
      </template>

      <template v-else-if="currentTab === 'system'">
        <section class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">系统信息</div>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">版本</div>
              <div class="text-white font-mono">{{ systemInfo.version }}</div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">HA 实体</div>
              <div class="text-white font-mono">{{ systemInfo.ha_entity_count }}</div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">HA 连接</div>
              <div class="font-mono" :class="haConnected ? 'text-emerald-400' : 'text-red-400'">{{ haConnected ? '已连接' : '未连接' }}</div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">MA 连接</div>
              <div class="font-mono" :class="maConnected ? 'text-emerald-400' : 'text-red-400'">{{ maConnected ? '已连接' : '未连接' }}</div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">MA 播放器</div>
              <div class="text-white font-mono">{{ systemInfo.ma_players }}</div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">WS 客户端</div>
              <div class="text-white font-mono">{{ systemInfo.ws_clients }}</div>
            </div>
          </div>
        </section>
      </template>
    </div>

    <div class="shrink-0 px-4 pb-4 pt-2 border-t border-white/10 flex items-center gap-3">
      <span class="text-xs" :class="saveStatusClass">{{ saveStatusText }}</span>
      <div class="flex-1"></div>
      <button
        class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-40"
        :disabled="saving || !isDirty"
        @click="saveSettings"
      >
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  settings: { type: Object, default: () => ({}) },
  haEntities: { type: Array, default: () => [] },
  haConnected: { type: Boolean, default: false },
  maConnected: { type: Boolean, default: false },
  maState: { type: Object, default: () => ({}) },
  systemStatus: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['save'])

const tabs = [
  { id: 'connection', label: '连接', icon: '🔌' },
  { id: 'display', label: '显示', icon: '🖥️' },
  { id: 'floorplan', label: '户型图', icon: '🗺️' },
  { id: 'system', label: '系统', icon: '⚙️' }
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
  entity_mapping: [],
  floor_plan_image: '',
  ha_token_masked: '',
  ma_token_masked: ''
})

const currentTab = ref('connection')
const saving = ref(false)
const saveStatus = ref('idle')
const isDirty = ref(false)
const localSettings = ref(defaultSettings())

const widgetLabels = {
  weather: '天气概览',
  stats: '室内温湿度',
  lights: '灯光快捷',
  climate: '空调快捷',
  battery: '低电量设备',
  offline: '离线设备',
  music: '音乐播放'
}

const lightIconOptions = [
  { value: 'bulb', label: '灯泡' },
  { value: 'ceiling', label: '吊灯' },
  { value: 'lamp', label: '台灯' },
  { value: 'spot', label: '射灯' },
  { value: 'strip', label: '灯带' }
]

watch(
  () => props.settings,
  (settings) => {
    localSettings.value = {
      ...defaultSettings(),
      ...settings,
      sidebar_widgets: {
        ...defaultSidebarWidgets,
        ...(settings?.sidebar_widgets || {})
      }
    }
  },
  { immediate: true, deep: true }
)

const allLights = computed(() => props.haEntities.filter((entity) => entity.entity_id.startsWith('light.')))
const allClimates = computed(() => props.haEntities.filter((entity) => entity.entity_id.startsWith('climate.')))
const allCovers = computed(() => props.haEntities.filter((entity) => entity.entity_id.startsWith('cover.')))
const batteryEntities = computed(() => props.haEntities.filter((entity) => entity.attributes?.device_class === 'battery'))
const allEntities = computed(() => props.haEntities)
const weatherEntities = computed(() => props.haEntities.filter((entity) => entity.entity_id.startsWith('weather.')))
const temperatureEntities = computed(() => props.haEntities.filter((entity) => entity.attributes?.device_class === 'temperature'))
const humidityEntities = computed(() => props.haEntities.filter((entity) => entity.attributes?.device_class === 'humidity'))

const groupedMappings = computed(() => {
  const groups = {}
  for (const item of localSettings.value.entity_mapping || []) {
    const type = entityTypeLabel(item.type || 'other')
    if (!groups[type]) groups[type] = []
    groups[type].push(item)
  }
  return groups
})

const clockFormatValue = computed({
  get: () => (localSettings.value.clock_24h ? '24' : '12'),
  set: (value) => {
    localSettings.value.clock_24h = value === '24'
  }
})

const allLightsSelected = computed(() => allLights.value.length > 0 && localSettings.value.selected_light_entities.length === allLights.value.length)
const allClimatesSelected = computed(() => allClimates.value.length > 0 && localSettings.value.selected_climate_entities.length === allClimates.value.length)
const allCoversSelected = computed(() => allCovers.value.length > 0 && localSettings.value.selected_cover_entities.length === allCovers.value.length)

const haConnectedText = computed(() => props.haConnected ? '已连接' : '未连接')
const maConnectedText = computed(() => props.maConnected ? '已连接' : '未连接')
const haConnectedClass = computed(() => props.haConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400')
const maConnectedClass = computed(() => props.maConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400')

const saveStatusText = computed(() => {
  if (saveStatus.value === 'success') return '已保存'
  if (saveStatus.value === 'error') return '保存失败'
  if (isDirty.value) return '有未保存的修改'
  return ''
})

const saveStatusClass = computed(() => {
  if (saveStatus.value === 'success') return 'text-emerald-400'
  if (saveStatus.value === 'error') return 'text-red-400'
  return 'text-white/30'
})

const systemInfo = computed(() => ({
  version: '1.0.0',
  ha_entity_count: props.haEntities.length,
  ma_players: (props.maState.players || []).length,
  ws_clients: props.systemStatus.ws_clients || 0
}))

const markDirty = () => {
  isDirty.value = true
}

const toggleAll = (type) => {
  if (type === 'light') {
    localSettings.value.selected_light_entities = allLightsSelected.value ? [] : allLights.value.map((entity) => entity.entity_id)
  } else if (type === 'climate') {
    localSettings.value.selected_climate_entities = allClimatesSelected.value ? [] : allClimates.value.map((entity) => entity.entity_id)
  } else if (type === 'cover') {
    localSettings.value.selected_cover_entities = allCoversSelected.value ? [] : allCovers.value.map((entity) => entity.entity_id)
  }
  markDirty()
}

const entityTypeIcon = (type) => {
  return {
    light: '💡',
    climate: '❄️',
    sensor: '🌡️',
    switch: '🔘',
    cover: '🪟',
    fan: '🌀',
    media: '🎵',
    other: '📦'
  }[type] || '📦'
}

const entityTypeLabel = (type) => {
  return {
    light: '灯光',
    climate: '空调',
    sensor: '传感器',
    switch: '开关',
    cover: '窗帘',
    fan: '风扇',
    media: '媒体',
    other: '其他'
  }[type] || '其他'
}

const removeMapping = (entityId) => {
  localSettings.value.entity_mapping = (localSettings.value.entity_mapping || []).filter((item) => item.entity_id !== entityId)
  markDirty()
}

const updateMappingIcon = (entityId, iconVariant) => {
  localSettings.value.entity_mapping = (localSettings.value.entity_mapping || []).map((item) =>
    item.entity_id === entityId ? { ...item, icon_variant: iconVariant } : item
  )
  markDirty()
}

const saveSettings = async () => {
  saving.value = true
  saveStatus.value = 'idle'

  try {
    const response = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(localSettings.value)
    })
    if (!response.ok) throw new Error(await response.text())

    const data = await response.json()
    saveStatus.value = 'success'
    isDirty.value = false
    emit('save', data.settings || localSettings.value)
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  } catch (error) {
    console.error('Save failed:', error)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-input {
  appearance: none;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.8rem;
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  color: white;
  outline: none;
  transition: all 0.2s ease;
}

.settings-input:focus {
  border-color: rgba(59, 130, 246, 0.45);
  background-color: rgba(255, 255, 255, 0.1);
}

.settings-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.settings-input option {
  background: #101827;
  color: #f8fafc;
}

.selection-list {
  max-height: 10rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.selection-item {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0.55rem;
  border-radius: 0.75rem;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
}

.selection-item:hover {
  background: rgba(255, 255, 255, 0.07);
}

.selection-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.settings-view {
  color: white;
}

.settings-view ::-webkit-scrollbar {
  width: 4px;
}

.settings-view ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
</style>
