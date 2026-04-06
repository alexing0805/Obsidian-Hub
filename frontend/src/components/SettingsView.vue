<template>
  <div class="settings-view p-5 overflow-y-auto h-full">
    <div class="max-w-2xl mx-auto space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold">系统设置</h2>
          <p class="text-xs text-white/40 mt-0.5">保存后自动重连</p>
        </div>
        <span class="text-xs px-2 py-1 rounded" :class="saveStatusClass">{{ saveStatusText }}</span>
      </div>

      <!-- HA Settings -->
      <div class="glass-effect rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-blue-600/30 flex items-center justify-center text-xs">🏠</div>
          <div>
            <h3 class="font-semibold text-sm">Home Assistant</h3>
            <p class="text-xs text-white/40">智能家居核心控制</p>
          </div>
          <div class="ml-auto">
            <span class="text-xs px-2 py-1 rounded" :class="haConnectedClass">{{ haConnectedText }}</span>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-xs text-white/60 mb-1">HA URL</label>
            <input v-model="settings.ha_url" type="text" placeholder="http://192.168.1.100:8123"
              class="settings-input w-full" @input="markDirty" />
          </div>
          <div>
            <label class="block text-xs text-white/60 mb-1">HA Token</label>
            <input v-model="settings.ha_token" type="password" placeholder="Long-Lived Access Token"
              class="settings-input w-full" @input="markDirty" />
          </div>
          <div class="flex items-center gap-3">
            <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
            <input v-model.number="settings.ha_refresh_interval" type="number" min="5" max="300"
              class="settings-input w-24" @input="markDirty" />
            <span class="text-xs text-white/40">秒</span>
          </div>
          <div class="flex items-center gap-3">
            <label class="text-xs text-white/60 w-20 shrink-0">温度实体</label>
            <select v-model="settings.temperature_entity" class="settings-input flex-1" @change="markDirty">
              <option value="">自动选择</option>
              <option v-for="e in temperatureEntities" :key="e.entity_id" :value="e.entity_id">
                {{ e.attributes?.friendly_name || e.entity_id }}
              </option>
            </select>
          </div>
          <div class="pt-1">
            <button class="px-4 py-2 text-sm rounded-lg border transition-colors"
              :class="haConnected ? 'border-blue-500/50 text-blue-400 hover:bg-blue-500/10' : 'border-white/10 text-white/40'"
              @click="testHAConnection">
              测试连接
            </button>
          </div>
        </div>
      </div>

      <!-- MA Settings -->
      <div class="glass-effect rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-purple-600/30 flex items-center justify-center text-xs">🎵</div>
          <div>
            <h3 class="font-semibold text-sm">Music Assistant</h3>
            <p class="text-xs text-white/40">音乐播放控制</p>
          </div>
          <div class="ml-auto">
            <span class="text-xs px-2 py-1 rounded" :class="maConnectedClass">{{ maConnectedText }}</span>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-xs text-white/60 mb-1">MA WebSocket URL</label>
            <input v-model="settings.ma_url" type="text" placeholder="ws://192.168.1.100:8095/ws"
              class="settings-input w-full" @input="markDirty" />
          </div>
          <div>
            <label class="block text-xs text-white/60 mb-1">MA Token</label>
            <input v-model="settings.ma_token" type="password" placeholder="长期访问令牌"
              class="settings-input w-full" @input="markDirty" />
          </div>
          <div class="flex items-center gap-3">
            <label class="text-xs text-white/60 w-20 shrink-0">刷新间隔</label>
            <input v-model.number="settings.ma_refresh_interval" type="number" min="2" max="60"
              class="settings-input w-24" @input="markDirty" />
            <span class="text-xs text-white/40">秒</span>
          </div>
          <div class="pt-1">
            <button class="px-4 py-2 text-sm rounded-lg border transition-colors"
              :class="maConnected ? 'border-purple-500/50 text-purple-400 hover:bg-purple-500/10' : 'border-white/10 text-white/40'"
              @click="testMAConnection">
              测试连接
            </button>
          </div>
        </div>
      </div>

      <!-- Light Mapping -->
      <div class="glass-effect rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-yellow-600/30 flex items-center justify-center text-xs">💡</div>
          <div>
            <h3 class="font-semibold text-sm">灯光映射</h3>
            <p class="text-xs text-white/40">将 HA 灯光映射到面板显示位置</p>
          </div>
        </div>

        <div class="space-y-2">
          <div v-for="(_, i) in 8" :key="i" class="flex items-center gap-2">
            <span class="text-xs text-white/40 w-5 shrink-0 text-right">#{{ i + 1 }}</span>
            <select v-model="settings.light_mapping[i]" class="settings-input flex-1" @change="markDirty">
              <option value="">-- 不映射 --</option>
              <option v-for="l in allLights" :key="l.entity_id" :value="l.entity_id">
                {{ l.attributes?.friendly_name || l.entity_id }}
              </option>
            </select>
            <div class="flex items-center gap-1 shrink-0">
              <input v-model.number="settings.light_positions[i][0]" type="number" min="0" max="800"
                class="settings-input w-16 text-center" @input="markDirty" />
              <span class="text-xs text-white/40">,</span>
              <input v-model.number="settings.light_positions[i][1]" type="number" min="0" max="600"
                class="settings-input w-16 text-center" @input="markDirty" />
            </div>
          </div>
          <p class="text-xs text-white/30 mt-2">位置对应楼层 SVG 视图 (800×600)，格式：X,Y</p>
        </div>
      </div>

      <!-- Display -->
      <div class="glass-effect rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-emerald-600/30 flex items-center justify-center text-xs">🖥️</div>
          <div>
            <h3 class="font-semibold text-sm">显示</h3>
            <p class="text-xs text-white/40">界面显示选项</p>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm">显示侧边栏</div>
              <div class="text-xs text-white/40">总览页右侧显示天气/音乐面板</div>
            </div>
            <button class="w-11 h-6 rounded-full transition-colors relative"
              :class="settings.show_sidebar ? 'bg-emerald-500' : 'bg-white/20'"
              @click="toggleSidebar">
              <div class="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform"
                :class="settings.show_sidebar ? 'translate-x-5.5' : 'translate-x-0.5'"></div>
            </button>
          </div>
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm">时钟格式</div>
            </div>
            <div class="flex gap-2">
              <button class="px-3 py-1 text-xs rounded-lg transition-colors"
                :class="settings.clock_24h ? 'bg-emerald-500/30 text-emerald-300' : 'bg-white/10 text-white/40'"
                @click="settings.clock_24h = true; markDirty()">24H</button>
              <button class="px-3 py-1 text-xs rounded-lg transition-colors"
                :class="!settings.clock_24h ? 'bg-emerald-500/30 text-emerald-300' : 'bg-white/10 text-white/40'"
                @click="settings.clock_24h = false; markDirty()">12H</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3">
        <button class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-40"
          :disabled="saving || !isDirty"
          @click="saveSettings">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
        <button class="px-5 py-2 border border-white/20 text-white/60 hover:text-white hover:border-white/40 rounded-lg text-sm transition-colors"
          @click="resetSettings">
          重置
        </button>
      </div>

      <!-- System Info -->
      <div class="glass-effect rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center text-xs">ℹ️</div>
          <h3 class="font-semibold text-sm">系统信息</h3>
        </div>
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
            <div class="text-white/40 mb-1">MA 播放器</div>
            <div class="text-white font-mono">{{ systemInfo.ma_players }}</div>
          </div>
          <div class="bg-white/5 rounded-lg p-3">
            <div class="text-white/40 mb-1">WS 客户端</div>
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

const saving = ref(false)
const saveStatus = ref('idle')
const isDirty = ref(false)

const defaultSettings = {
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
  clock_24h: true
}

const settings = ref({ ...defaultSettings })

const allLights = computed(() =>
  props.haEntities.filter(e => e.entity_id.startsWith('light.'))
)
const temperatureEntities = computed(() =>
  props.haEntities.filter(e => {
    const a = e.attributes || {}
    return a.device_class === 'temperature' || e.entity_id.includes('temperature')
  })
)

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

const markDirty = () => { isDirty.value = true }

const toggleSidebar = () => {
  settings.value.show_sidebar = !settings.value.show_sidebar
  isDirty.value = true
  emit('toggle-sidebar', settings.value.show_sidebar)
}

const saveSettings = async () => {
  saving.value = true
  saveStatus.value = 'idle'
  try {
    const r = await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value)
    })
    if (!r.ok) throw new Error(await r.text())
    saveStatus.value = 'success'
    isDirty.value = false
    emit('save', settings.value)
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
  } catch (e) {
    console.error('Save failed:', e)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = 'idle' }, 3000)
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
    const r = await fetch('/api/status')
    const d = await r.json()
    const s = d.status || {}
    const msg = s.ha_connected
      ? `✅ HA 已连接\n实体数: ${s.ha_entity_count}`
      : `❌ HA 未连接，请检查 URL 和 Token`
    alert(msg)
  } catch {
    alert('❌ HA 连接失败')
  }
}

const testMAConnection = async () => {
  try {
    const r = await fetch('/api/status')
    const d = await r.json()
    const s = d.status || {}
    const msg = s.ma_connected ? '✅ MA 已连接' : '❌ MA 未连接，请检查 URL 和 Token'
    alert(msg)
  } catch {
    alert('❌ MA 连接失败')
  }
}

const restartService = () => {
  if (confirm('确定要重启服务吗？')) emit('restart')
}

const loadSettings = async () => {
  try {
    const r = await fetch('/api/settings')
    if (r.ok) {
      const data = await r.json()
      settings.value = { ...defaultSettings, ...data.settings }
    }
  } catch (e) {
    console.error('Failed to load settings:', e)
  }
  emit('settings-loaded', { ...settings.value })
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
