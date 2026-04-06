<template>
  <div class="settings-view p-6 overflow-y-auto h-full">
    <div class="max-w-2xl mx-auto space-y-6">

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold">系统设置</h2>
          <p class="text-xs text-white/40 mt-1">配置 Home Assistant 与 Music Assistant 连接</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="status-badge text-xs px-2 py-1 rounded" :class="saveStatusClass">{{ saveStatusText }}</span>
        </div>
      </div>

      <!-- HA Settings -->
      <div class="glass-effect rounded-xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-blue-600/30 flex items-center justify-center text-sm">🏠</div>
          <div>
            <h3 class="font-semibold text-sm">Home Assistant</h3>
            <p class="text-xs text-white/40">智能家居核心控制</p>
          </div>
          <div class="ml-auto">
            <span class="text-xs px-2 py-1 rounded" :class="haConnectedClass">{{ haConnectedText }}</span>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs text-white/60 mb-1.5">HA URL</label>
            <input
              v-model="settings.ha_url"
              type="text"
              placeholder="http://192.168.100.50:8123"
              class="settings-input"
              @input="markDirty"
            />
          </div>

          <div>
            <label class="block text-xs text-white/60 mb-1.5">HA Token</label>
            <div class="relative">
              <input
                v-model="settings.ha_token"
                :type="showHaToken ? 'text' : 'password'"
                placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                class="settings-input pr-10"
                @input="markDirty"
              />
              <button
                class="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                @click="showHaToken = !showHaToken"
              >
                {{ showHaToken ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-white/60 mb-1.5">实体刷新间隔 (秒)</label>
              <input
                v-model.number="settings.ha_refresh_interval"
                type="number"
                min="5"
                max="300"
                class="settings-input"
                @input="markDirty"
              />
            </div>
            <div>
              <label class="block text-xs text-white/60 mb-1.5">温度实体</label>
              <select v-model="settings.temperature_entity" class="settings-input" @change="markDirty">
                <option value="">自动选择</option>
                <option v-for="entity in temperatureEntities" :key="entity.entity_id" :value="entity.entity_id">
                  {{ entity.attributes?.friendly_name || entity.entity_id }}
                </option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs text-white/60 mb-1.5">湿度实体</label>
            <select v-model="settings.humidity_entity" class="settings-input" @change="markDirty">
              <option value="">自动选择</option>
              <option v-for="entity in humidityEntities" :key="entity.entity_id" :value="entity.entity_id">
                {{ entity.attributes?.friendly_name || entity.entity_id }}
              </option>
            </select>
          </div>

          <div>
            <button
              class="px-4 py-2 text-sm rounded-lg border transition-colors"
              :class="haConnected ? 'border-blue-500/50 text-blue-400 hover:bg-blue-500/10' : 'border-white/10 text-white/40'"
              :disabled="!haConnected"
              @click="testHAConnection"
            >
              测试连接
            </button>
          </div>
        </div>
      </div>

      <!-- MA Settings -->
      <div class="glass-effect rounded-xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-purple-600/30 flex items-center justify-center text-sm">🎵</div>
          <div>
            <h3 class="font-semibold text-sm">Music Assistant</h3>
            <p class="text-xs text-white/40">音乐播放控制</p>
          </div>
          <div class="ml-auto">
            <span class="text-xs px-2 py-1 rounded" :class="maConnectedClass">{{ maConnectedText }}</span>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs text-white/60 mb-1.5">MA WebSocket URL</label>
            <input
              v-model="settings.ma_url"
              type="text"
              placeholder="ws://192.168.100.50:8095/ws"
              class="settings-input"
              @input="markDirty"
            />
          </div>

          <div>
            <label class="block text-xs text-white/60 mb-1.5">MA Token</label>
            <div class="relative">
              <input
                v-model="settings.ma_token"
                :type="showMaToken ? 'text' : 'password'"
                placeholder="长期令牌"
                class="settings-input pr-10"
                @input="markDirty"
              />
              <button
                class="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                @click="showMaToken = !showMaToken"
              >
                {{ showMaToken ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-xs text-white/60 mb-1.5">队列刷新间隔 (秒)</label>
            <input
              v-model.number="settings.ma_refresh_interval"
              type="number"
              min="2"
              max="60"
              class="settings-input"
              @input="markDirty"
            />
          </div>

          <div>
            <button
              class="px-4 py-2 text-sm rounded-lg border transition-colors"
              :class="maConnected ? 'border-purple-500/50 text-purple-400 hover:bg-purple-500/10' : 'border-white/10 text-white/40'"
              :disabled="!maConnected"
              @click="testMAConnection"
            >
              测试连接
            </button>
          </div>
        </div>
      </div>

      <!-- Light Mapping -->
      <div class="glass-effect rounded-xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-yellow-600/30 flex items-center justify-center text-sm">💡</div>
          <div>
            <h3 class="font-semibold text-sm">灯光映射</h3>
            <p class="text-xs text-white/40">将 HA 灯光映射到面板显示位置</p>
          </div>
        </div>

        <div class="space-y-2">
          <div
            v-for="(pos, index) in lightPositions"
            :key="index"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-white/40 w-6 text-right">#{{ index + 1 }}</span>
            <select
              v-model="settings.light_mapping[index]"
              class="settings-input flex-1"
              @change="markDirty"
            >
              <option value="">-- 不映射 --</option>
              <option v-for="light in allLights" :key="light.entity_id" :value="light.entity_id">
                {{ light.attributes?.friendly_name || light.entity_id }}
              </option>
            </select>
            <div class="flex items-center gap-1">
              <span class="text-xs text-white/40">X:</span>
              <input
                v-model.number="settings.light_positions[index].x"
                type="number"
                min="0"
                max="800"
                class="settings-input w-16 text-center"
                @input="markDirty"
              />
              <span class="text-xs text-white/40">Y:</span>
              <input
                v-model.number="settings.light_positions[index].y"
                type="number"
                min="0"
                max="600"
                class="settings-input w-16 text-center"
                @input="markDirty"
              />
            </div>
          </div>
          <p class="text-xs text-white/30 mt-2">位置坐标对应楼层 SVG 视图 (800×600)。点击"保存"后生效。</p>
        </div>
      </div>

      <!-- Display Settings -->
      <div class="glass-effect rounded-xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-emerald-600/30 flex items-center justify-center text-sm">🖥️</div>
          <div>
            <h3 class="font-semibold text-sm">显示</h3>
            <p class="text-xs text-white/40">界面显示选项</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm">显示侧边栏</div>
              <div class="text-xs text-white/40">在右侧显示天气、音乐控制面板</div>
            </div>
            <button
              class="w-12 h-6 rounded-full transition-colors relative"
              :class="settings.show_sidebar ? 'bg-emerald-500' : 'bg-white/20'"
              @click="toggleSidebar"
            >
              <div
                class="absolute top-1 w-4 h-4 rounded-full bg-white transition-transform"
                :class="settings.show_sidebar ? 'translate-x-7' : 'translate-x-1'"
              ></div>
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm">时钟格式</div>
              <div class="text-xs text-white/40">24小时制 / 12小时制</div>
            </div>
            <div class="flex gap-2">
              <button
                class="px-3 py-1 text-xs rounded-lg transition-colors"
                :class="settings.clock_24h ? 'bg-emerald-500/30 text-emerald-300' : 'bg-white/10 text-white/40'"
                @click="setClockFormat(true)"
              >24H</button>
              <button
                class="px-3 py-1 text-xs rounded-lg transition-colors"
                :class="!settings.clock_24h ? 'bg-emerald-500/30 text-emerald-300' : 'bg-white/10 text-white/40'"
                @click="setClockFormat(false)"
              >12H</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 pt-2">
        <button
          class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-40"
          :disabled="!isDirty || saving"
          @click="saveSettings"
        >
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
        <button
          class="px-6 py-2.5 border border-white/20 text-white/60 hover:text-white hover:border-white/40 rounded-lg text-sm transition-colors"
          :disabled="!isDirty"
          @click="resetSettings"
        >
          重置
        </button>
        <button
          class="px-6 py-2.5 border border-white/10 text-white/30 hover:text-white/50 rounded-lg text-sm transition-colors ml-auto"
          @click="restartService"
        >
          重启服务
        </button>
      </div>

      <!-- System Info -->
      <div class="glass-effect rounded-xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-sm">ℹ️</div>
          <div>
            <h3 class="font-semibold text-sm">系统信息</h3>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="bg-white/5 rounded-lg p-3">
            <div class="text-white/40 mb-1">版本</div>
            <div class="text-white font-mono">{{ systemInfo.version }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-3">
            <div class="text-white/40 mb-1">HA 实体数</div>
            <div class="text-white font-mono">{{ systemInfo.ha_entity_count }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-3">
            <div class="text-white/40 mb-1">MA 播放器</div>
            <div class="text-white font-mono">{{ systemInfo.ma_players }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-3">
            <div class="text-white/40 mb-1">WebSocket 客户端</div>
            <div class="text-white font-mono">{{ systemInfo.ws_clients }}</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  haEntities: { type: Array, default: () => [] },
  haConnected: { type: Boolean, default: false },
  maConnected: { type: Boolean, default: false },
  maState: { type: Object, default: () => ({}) },
  systemStatus: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['save', 'restart', 'toggle-sidebar', 'settings-loaded'])

const showHaToken = ref(false)
const showMaToken = ref(false)
const isDirty = ref(false)
const saving = ref(false)
const saveStatus = ref('idle') // idle | success | error

const defaultSettings = {
  ha_url: '',
  ha_token: '',
  ha_refresh_interval: 15,
  temperature_entity: '',
  humidity_entity: '',
  ma_url: '',
  ma_token: '',
  ma_refresh_interval: 5,
  light_mapping: Array(8).fill(''),
  light_positions: Array(8).fill(null).map(() => ({ x: 0, y: 0 })),
  show_sidebar: true,
  clock_24h: true
}

const settings = ref({ ...defaultSettings })

const allLights = computed(() =>
  props.haEntities.filter(e => e.entity_id.startsWith('light.'))
)

const temperatureEntities = computed(() =>
  props.haEntities.filter(e => {
    const attrs = e.attributes || {}
    return attrs.device_class === 'temperature' || e.entity_id.includes('temperature')
  })
)

const humidityEntities = computed(() =>
  props.haEntities.filter(e => {
    const attrs = e.attributes || {}
    return attrs.device_class === 'humidity' || e.entity_id.includes('humidity')
  })
)

const lightPositions = computed(() => settings.value.light_positions)

// Initialize light positions from parent if available
const initLightPositions = () => {
  const parentPositions = window.__OBSIDIAN_HUB_LIGHT_POSITIONS__
  if (parentPositions && Array.isArray(parentPositions)) {
    settings.value.light_positions = parentPositions.map(p =>
      Array.isArray(p) ? { x: p[0], y: p[1] } : { x: 0, y: 0 }
    )
  }
}

const haConnectedText = computed(() => props.haConnected ? '已连接' : '未连接')
const maConnectedText = computed(() => props.maConnected ? '已连接' : '未连接')
const haConnectedClass = computed(() =>
  props.haConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
)
const maConnectedClass = computed(() =>
  props.maConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
)

const saveStatusText = computed(() => {
  if (saveStatus.value === 'success') return '已保存'
  if (saveStatus.value === 'error') return '保存失败'
  return ''
})

const saveStatusClass = computed(() => {
  if (saveStatus.value === 'success') return 'bg-emerald-500/20 text-emerald-400'
  if (saveStatus.value === 'error') return 'bg-red-500/20 text-red-400'
  return ''
})

const systemInfo = computed(() => ({
  version: '1.0.0',
  ha_entity_count: props.haEntities.length,
  ma_players: (props.maState.players || []).length,
  ws_clients: props.systemStatus.ws_clients || 0
}))

const markDirty = () => {
  isDirty.value = true
  saveStatus.value = 'idle'
}

const toggleSidebar = () => {
  settings.value.show_sidebar = !settings.value.show_sidebar
  emit('toggle-sidebar', settings.value.show_sidebar)
  markDirty()
}

const setClockFormat = (is24h) => {
  settings.value.clock_24h = is24h
  markDirty()
}

const saveSettings = async () => {
  saving.value = true
  saveStatus.value = 'idle'
  try {
    const response = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value)
    })
    if (!response.ok) throw new Error('Save failed')
    saveStatus.value = 'success'
    isDirty.value = false
    emit('save', { ...settings.value })
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  } catch (error) {
    console.error('Failed to save settings:', error)
    saveStatus.value = 'error'
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  settings.value = { ...defaultSettings }
  isDirty.value = true
}

const testHAConnection = async () => {
  try {
    const response = await fetch('/api/status')
    const data = await response.json()
    alert(data.status?.ha_connected ? '✅ HA 连接正常' : '❌ HA 连接失败')
  } catch {
    alert('❌ HA 连接失败')
  }
}

const testMAConnection = async () => {
  try {
    const response = await fetch('/api/status')
    const data = await response.json()
    alert(data.status?.ma_connected ? '✅ MA 连接正常' : '❌ MA 连接失败')
  } catch {
    alert('❌ MA 连接失败')
  }
}

const restartService = () => {
  if (confirm('确定要重启服务吗？这将短暂中断连接。')) {
    emit('restart')
  }
}

const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    if (response.ok) {
      const data = await response.json()
      if (data.settings) {
        settings.value = { ...defaultSettings, ...data.settings }
      }
    }
  } catch {
    // Use defaults if API not available
  }
  initLightPositions()
  emit('settings-loaded', { ...settings.value })
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-input {
  @apply w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white;
  @apply focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-colors;
}
.settings-input::placeholder {
  @apply text-white/25;
}
.settings-view {
  color: white;
}
.settings-view ::-webkit-scrollbar {
  width: 4px;
}
.settings-view ::-webkit-scrollbar-track {
  background: transparent;
}
.settings-view ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
</style>
