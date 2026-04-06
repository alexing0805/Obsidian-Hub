<template>
  <div class="settings-view flex flex-col h-full">

    <!-- 顶部 Tab 导航 -->
    <div class="shrink-0 px-4 pt-4 pb-2 flex items-center gap-1 border-b border-white/10">
      <button
        v-for="tab in tabs" :key="tab.id"
        class="px-3 py-1.5 text-xs rounded-lg transition-colors"
        :class="currentTab === tab.id ? 'bg-white/15 text-white' : 'text-white/40 hover:text-white/70'"
        @click="currentTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- 内容区（可滚动） -->
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4">

      <!-- 连接设置 -->
      <template v-if="currentTab === 'connection'">
        <div class="glass-effect rounded-xl p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-lg bg-blue-600/30 flex items-center justify-center text-xs">🏠</div>
            <div class="font-semibold text-sm">Home Assistant</div>
            <div class="ml-auto">
              <span class="text-xs px-2 py-1 rounded" :class="haConnectedClass">{{ haConnectedText }}</span>
            </div>
          </div>
          <div class="space-y-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">HA URL</label>
              <input v-model="localSettings.ha_url" type="text" placeholder="http://192.168.1.100:8123"
                class="settings-input w-full" @input="markDirty" />
            </div>
            <div>
              <label class="block text-xs text-white/60 mb-1">HA Token</label>
              <input v-model="localSettings.ha_token" type="password" placeholder="Long-Lived Access Token"
                class="settings-input w-full" @input="markDirty" />
            </div>
            <div class="flex items-center gap-3">
              <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
              <input v-model.number="localSettings.ha_refresh_interval" type="number" min="5" max="300"
                class="settings-input w-24" @input="markDirty" />
              <span class="text-xs text-white/40">秒</span>
            </div>
            <div>
              <button class="px-4 py-2 text-sm rounded-lg border transition-colors"
                :class="haConnected ? 'border-blue-500/50 text-blue-400 hover:bg-blue-500/10' : 'border-white/10 text-white/40'"
                @click="testHAConnection">
                测试连接
              </button>
            </div>
          </div>
        </div>

        <div class="glass-effect rounded-xl p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-lg bg-purple-600/30 flex items-center justify-center text-xs">🎵</div>
            <div class="font-semibold text-sm">Music Assistant</div>
            <div class="ml-auto">
              <span class="text-xs px-2 py-1 rounded" :class="maConnectedClass">{{ maConnectedText }}</span>
            </div>
          </div>
          <div class="space-y-3">
            <div>
              <label class="block text-xs text-white/60 mb-1">MA WebSocket URL</label>
              <input v-model="localSettings.ma_url" type="text" placeholder="ws://192.168.1.100:8095/ws"
                class="settings-input w-full" @input="markDirty" />
            </div>
            <div>
              <label class="block text-xs text-white/60 mb-1">MA Token</label>
              <input v-model="localSettings.ma_token" type="password" placeholder="长期访问令牌"
                class="settings-input w-full" @input="markDirty" />
            </div>
            <div class="flex items-center gap-3">
              <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
              <input v-model.number="localSettings.ma_refresh_interval" type="number" min="2" max="60"
                class="settings-input w-24" @input="markDirty" />
              <span class="text-xs text-white/40">秒</span>
            </div>
            <div>
              <button class="px-4 py-2 text-sm rounded-lg border transition-colors"
                :class="maConnected ? 'border-purple-500/50 text-purple-400 hover:bg-purple-500/10' : 'border-white/10 text-white/40'"
                @click="testMAConnection">
                测试连接
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- 显示设置 -->
      <template v-if="currentTab === 'display'">
        <!-- 主页侧边栏控件 -->
        <div class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">🏠 主页侧边栏控件</div>
          <div class="text-xs text-white/40 mb-3">勾选要在主页侧边栏显示的控件，点击卡片可查看详情</div>
          <div class="space-y-2">
            <label v-for="(label, key) in widgetLabels" :key="key" class="flex items-center gap-3 cursor-pointer group">
              <input type="checkbox" v-model="localSettings.sidebar_widgets[key]"
                class="w-4 h-4 rounded accent-emerald-500" @change="markDirty" />
              <span class="text-sm text-white/70 group-hover:text-white transition-colors">{{ label }}</span>
            </label>
          </div>
        </div>

        <!-- 天气实体选择 -->
        <div class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">🌤️ 天气显示实体</div>
          <select v-model="localSettings.weather_entity_id" class="settings-input w-full" @change="markDirty">
            <option value="">自动（第一个天气实体）</option>
            <option v-for="w in weatherEntities" :key="w.entity_id" :value="w.entity_id">
              {{ w.attributes?.friendly_name || w.entity_id }}
            </option>
          </select>
          <div v-if="!weatherEntities.length" class="text-xs text-white/30 mt-2">未检测到天气实体，请先连接 HA</div>
        </div>

        <!-- 侧边栏开关 -->
        <div class="glass-effect rounded-xl p-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium">显示侧边栏</div>
              <div class="text-xs text-white/40 mt-0.5">关闭后主页不显示右侧面板</div>
            </div>
            <button class="w-11 h-6 rounded-full transition-colors relative shrink-0"
              :class="localSettings.show_sidebar ? 'bg-emerald-500' : 'bg-white/20'"
              @click="localSettings.show_sidebar = !localSettings.show_sidebar; markDirty()">
              <div class="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform"
                :class="localSettings.show_sidebar ? 'translate-x-5.5' : 'translate-x-0.5'"></div>
            </button>
          </div>
        </div>

        <!-- 时钟格式 -->
        <div class="glass-effect rounded-xl p-4">
          <div class="text-sm font-medium mb-3">时钟格式</div>
          <div class="flex gap-2">
            <button class="px-4 py-2 text-sm rounded-lg transition-colors"
              :class="localSettings.clock_24h ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/50' : 'bg-white/10 text-white/40 border border-transparent'"
              @click="localSettings.clock_24h = true; markDirty()">24 小时制</button>
            <button class="px-4 py-2 text-sm rounded-lg transition-colors"
              :class="!localSettings.clock_24h ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/50' : 'bg-white/10 text-white/40 border border-transparent'"
              @click="localSettings.clock_24h = false; markDirty()">12 小时制</button>
          </div>
        </div>
      </template>

      <!-- 灯光映射 -->
      <template v-if="currentTab === 'lights'">
        <div class="glass-effect rounded-xl p-4">
          <div class="text-xs text-white/40 mb-3">点击灯光可切换开关。映射保存在服务器端。</div>
          <div class="space-y-2">
            <div v-for="(_, i) in 8" :key="i" class="flex items-center gap-2">
              <span class="text-xs text-white/40 w-5 shrink-0 text-right">#{{ i + 1 }}</span>
              <select v-model="localSettings.light_mapping[i]" class="settings-input flex-1" @change="markDirty">
                <option value="">-- 不映射 --</option>
                <option v-for="l in allLights" :key="l.entity_id" :value="l.entity_id">
                  {{ l.attributes?.friendly_name || l.entity_id }}
                </option>
              </select>
              <div class="flex items-center gap-1 shrink-0">
                <input v-model.number="localSettings.light_positions[i][0]" type="number" min="0" max="800"
                  class="settings-input w-16 text-center" @input="markDirty" />
                <span class="text-xs text-white/40">,</span>
                <input v-model.number="localSettings.light_positions[i][1]" type="number" min="0" max="600"
                  class="settings-input w-16 text-center" @input="markDirty" />
              </div>
            </div>
          </div>
          <div class="mt-3 text-xs text-white/30">位置对应楼层 SVG 视图 (800×600)，格式：X,Y</div>
        </div>
      </template>

      <!-- 系统 -->
      <template v-if="currentTab === 'system'">
        <div class="glass-effect rounded-xl p-4">
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
              <div class="font-mono" :class="haConnected ? 'text-emerald-400' : 'text-red-400'">
                {{ haConnected ? '已连接' : '未连接' }}
              </div>
            </div>
            <div class="bg-white/5 rounded-lg p-3">
              <div class="text-white/40 mb-1">MA 连接</div>
              <div class="font-mono" :class="maConnected ? 'text-emerald-400' : 'text-red-400'">
                {{ maConnected ? '已连接' : '未连接' }}
              </div>
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
        </div>
      </template>

    </div>

    <!-- 底部保存按钮 -->
    <div class="shrink-0 px-4 pb-4 pt-2 border-t border-white/10 flex items-center gap-3">
      <span class="text-xs" :class="saveStatusClass">{{ saveStatusText }}</span>
      <div class="flex-1"></div>
      <button class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-40"
        :disabled="saving || !isDirty" @click="saveSettings">
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
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
  systemStatus: { type: Object, default: () => ({}) },
  sidebarWidgets: { type: Object, default: () => ({}) },
  weatherEntityId: { type: String, default: '' },
})

const emit = defineEmits(['save', 'restart', 'toggle-sidebar', 'settings-loaded'])

const tabs = [
  { id: 'connection', label: '连接', icon: '🔗' },
  { id: 'display', label: '显示', icon: '🖥️' },
  { id: 'lights', label: '灯光', icon: '💡' },
  { id: 'system', label: '系统', icon: 'ℹ️' },
]

const currentTab = ref('connection')
const saving = ref(false)
const saveStatus = ref('idle')
const isDirty = ref(false)

const widgetLabels = {
  weather: '🌤️ 天气概览',
  stats: '📊 统计概览',
  lights: '💡 灯光快捷',
  climate: '❄️ 空调快捷',
  battery: '🔋 低电量',
  offline: '📡 离线设备',
  music: '🎵 音乐播放',
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
  light_mapping: Array(8).fill(''),
  light_positions: [[140,130],[240,170],[560,130],[660,170],[120,350],[280,430],[430,390],[620,350]],
  show_sidebar: true,
  clock_24h: true,
  sidebar_widgets: {
    weather: true, stats: true, lights: true, climate: true,
    battery: true, offline: true, music: true
  },
  weather_entity_id: '',
})

const localSettings = ref(defaultSettings())

const allLights = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('light.')))
const weatherEntities = computed(() => props.haEntities.filter(e => e.entity_id.startsWith('weather.')))

const haConnectedText = computed(() => props.haConnected ? '已连接' : '未连接')
const maConnectedText = computed(() => props.maConnected ? '已连接' : '未连接')
const haConnectedClass = computed(() => props.haConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400')
const maConnectedClass = computed(() => props.maConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400')
const saveStatusText = computed(() => {
  if (saveStatus.value === 'success') return '已保存，自动重连中...'
  if (saveStatus.value === 'error') return '保存失败'
  if (isDirty.value) return '有未保存的更改'
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

const markDirty = () => { isDirty.value = true }

const saveSettings = async () => {
  saving.value = true
  saveStatus.value = 'idle'
  try {
    const r = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(localSettings.value)
    })
    if (!r.ok) throw new Error(await r.text())
    saveStatus.value = 'success'
    isDirty.value = false
    emit('save', localSettings.value)
    setTimeout(() => { saveStatus.value = 'idle' }, 4000)
  } catch (e) {
    console.error('Save failed:', e)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  } finally {
    saving.value = false
  }
}

const testHAConnection = () => {
  const msg = props.haConnected
    ? `✅ HA 已连接\n实体数: ${props.haEntities.length}`
    : `❌ HA 未连接\n请检查 URL 和 Token`
  alert(msg)
}

const testMAConnection = () => {
  const msg = props.maConnected ? '✅ MA 已连接' : '❌ MA 未连接\n请检查 URL 和 Token'
  alert(msg)
}

const loadSettings = async () => {
  try {
    const r = await fetch('/api/settings')
    if (r.ok) {
      const data = await r.json()
      const s = data.settings || {}
      localSettings.value = {
        ...defaultSettings(),
        ha_url: s.ha_url || '',
        ha_token: s.ha_token || '',
        ma_url: s.ma_url || '',
        ma_token: s.ma_token || '',
        ha_refresh_interval: s.ha_refresh_interval || 15,
        ma_refresh_interval: s.ma_refresh_interval || 5,
        temperature_entity: s.temperature_entity || '',
        humidity_entity: s.humidity_entity || '',
        light_mapping: s.light_mapping || Array(8).fill(''),
        light_positions: s.light_positions || [[140,130],[240,170],[560,130],[660,170],[120,350],[280,430],[430,390],[620,350]],
        show_sidebar: s.show_sidebar !== undefined ? s.show_sidebar : true,
        clock_24h: s.clock_24h !== undefined ? s.clock_24h : true,
        sidebar_widgets: s.sidebar_widgets || { weather: true, stats: true, lights: true, climate: true, battery: true, offline: true, music: true },
        weather_entity_id: s.weather_entity_id || '',
      }
    }
  } catch (e) {
    console.error('Failed to load settings:', e)
  }
  emit('settings-loaded', localSettings.value)
}

onMounted(loadSettings)
</script>

<style scoped>
.settings-input {
  @apply bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white;
  @apply focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-colors;
}
.settings-input::placeholder { @apply text-white/25; }
.settings-view { color: white; }
.settings-view ::-webkit-scrollbar { width: 4px; }
.settings-view ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
</style>
