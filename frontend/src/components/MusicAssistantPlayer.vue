<template>
  <div class="p-1 flex flex-col min-h-0 h-full overflow-y-auto">
    <div class="glass-panel rounded-[2rem] p-5 flex flex-col h-full min-h-0 relative overflow-hidden group shadow-2xl ring-1 ring-white/10 bg-gradient-to-br from-white/10 to-transparent">

      <div v-if="playState === 'playing'" class="absolute inset-0 bg-cyan-500/5 blur-3xl -z-10 animate-pulse transition-opacity duration-1000"></div>

      <!-- 1. 顶部：播放器选择 + 状态 -->
      <div class="flex items-center justify-between gap-3 mb-4 relative z-10 shrink-0">
        <div class="relative flex-1 min-w-0">
          <button
            class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all text-left w-full group/btn"
            @click="showSelector = !showSelector"
          >
            <div class="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.5)] shrink-0" :class="maConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'"></div>
            <span class="text-sm font-bold text-white/70 uppercase tracking-tight truncate flex-1">
              {{ activePlayerName || '选择播放器' }}
            </span>
            <span class="text-xs text-white/20 group-hover/btn:text-white/40 transition-colors shrink-0">▼</span>
          </button>

          <div v-if="showSelector" class="absolute left-0 top-full mt-2 w-full z-50 bg-neutral-900/98 backdrop-blur-3xl rounded-2xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] py-2 max-h-[280px] overflow-y-auto animate-fade-in ring-1 ring-white/5">
            <div
              v-for="p in maState.players || []" :key="p.player_id"
              class="px-4 py-3 text-sm font-bold cursor-pointer hover:bg-white/10 transition-colors flex items-center justify-between"
              :class="maState.active_player_id === p.player_id ? 'text-cyan-400 bg-cyan-400/10' : 'text-white/60'"
              @click="onSelectPlayer(p)"
            >
              <span>{{ p.friendly_name || p.name }}</span>
              <div v-if="p.playback_state === 'playing'" class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
            </div>
            <div v-if="!(maState.players || []).length" class="px-4 py-3 text-sm text-white/30 italic">No players available</div>
          </div>
        </div>
        <span class="text-xs text-white/20 font-black uppercase tracking-[0.1em] truncate max-w-[60px] bg-white/5 px-2 py-1 rounded-md border border-white/5 shrink-0">{{ queueLabel }}</span>
      </div>

      <!-- 2. 封面图（响应式，最大 180px） -->
      <div class="flex justify-center mb-4 shrink-0">
        <div class="w-full max-w-[180px] aspect-square rounded-[1.5rem] overflow-hidden relative shadow-2xl ring-2 ring-white/10 bg-black/40 group-hover:scale-105 transition-transform duration-500">
          <img :src="artworkUrl || fallbackArtwork" alt="Cover" class="w-full h-full object-cover transition-opacity duration-700" :class="artworkUrl ? 'opacity-100' : 'opacity-20'" />
          <div v-if="playState === 'playing'" class="absolute bottom-3 right-3 p-2 bg-black/60 backdrop-blur-xl rounded-full border border-white/10 shadow-lg">
             <div class="flex gap-0.5 items-end h-4 w-4 justify-center">
                <span class="w-0.5 bg-cyan-400 animate-[music-bar_1.2s_infinite] music-bar-item" style="height:30%"></span>
                <span class="w-0.5 bg-cyan-400 animate-[music-bar_1.2s_0.2s_infinite] music-bar-item" style="height:80%"></span>
                <span class="w-0.5 bg-cyan-400 animate-[music-bar_1.2s_0.4s_infinite] music-bar-item" style="height:55%"></span>
             </div>
          </div>
        </div>
      </div>

      <!-- 3. 曲目信息 -->
      <div class="text-center mb-4 shrink-0 px-2">
        <h3 class="font-black text-base leading-tight text-white mb-1.5 tracking-tight group-hover:text-cyan-400 transition-colors line-clamp-1">{{ trackName || 'Ready to Play' }}</h3>
        <p class="text-xs font-bold text-white/40 tracking-[0.05em] truncate uppercase">{{ artistName || 'Music Assistant' }}</p>
      </div>

      <!-- 4. 进度条 -->
      <div class="flex items-center gap-3 px-2 mb-4 shrink-0">
        <span class="text-xs font-black text-white/30 tabular-nums w-9 shrink-0">{{ formatTime(currentElapsed) }}</span>
        <div class="progress-bar-track flex-1 h-2 bg-white/5 rounded-full cursor-pointer relative hover:h-2.5 transition-all group/progress" @click="onProgressClick" @mousedown.prevent="onProgressMouseDown">
          <div class="h-full bg-cyan-500 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.5)]" :style="{ width: progressPercent + '%' }"></div>
          <div class="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full border-2 border-cyan-500 shadow-xl opacity-0 group-hover/progress:opacity-100 transition-opacity -ml-2" :style="{ left: progressPercent + '%' }"></div>
        </div>
        <span class="text-xs font-black text-white/30 tabular-nums w-9 text-right shrink-0">{{ formatTime(duration) }}</span>
      </div>

      <!-- 5. 播放控制 -->
      <div class="flex items-center justify-center gap-8 mb-4 shrink-0">
        <button class="text-white/30 hover:text-white transition-all active:scale-75 disabled:opacity-10" :disabled="!activeQueueId" @click="prevTrack">
          <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
        </button>
        <button class="w-14 h-14 flex items-center justify-center bg-white text-black rounded-2xl shadow-xl hover:scale-105 active:scale-95 transition-all disabled:opacity-10" :disabled="!activeQueueId" @click="togglePlay">
          <svg v-if="playState === 'playing'" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          <svg v-else class="w-6 h-6 translate-x-[2px]" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <button class="text-white/30 hover:text-white transition-all active:scale-75 disabled:opacity-10" :disabled="!activeQueueId" @click="nextTrack">
          <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
        </button>
      </div>

      <!-- 6. 音量条 -->
      <div class="flex items-center gap-3 px-4 shrink-0">
        <svg class="w-4 h-4 text-white/20 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536l-3.536 3.536L2 20h2.828l3.536-3.536M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        <div class="volume-track relative flex-1 h-1.5 bg-white/5 rounded-full cursor-pointer group/vol" @click="onVolumeClick" @mousedown.prevent="onVolumeMouseDown">
          <div class="h-full bg-white/40 rounded-full" :style="{ width: displayedVolume + '%' }"></div>
          <div class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover/vol:opacity-100 transition-opacity -ml-1.5" :style="{ left: displayedVolume + '%' }"></div>
        </div>
        <span class="text-xs font-black text-white/30 tabular-nums w-7 text-right shrink-0">{{ displayedVolume }}</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  maState: { type: Object, default: () => ({}) }
})

const fallbackArtwork =
  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cmVjdCBmaWxsPSIjMWUyOTNiIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNGI1NTYzIiBmb250LXNpemU9IjQwIj7imao8L3RleHQ+PC9zdmc+'

const emit = defineEmits(['select-player'])

const showSelector = ref(false)
const activePlayerName = computed(() => {
  if (!props.maState?.active_player_id) return '选择播放器'
  const p = (props.maState.players || []).find(p => p.player_id === props.maState.active_player_id)
  return p ? (p.friendly_name || p.name) : '选择播放器'
})

const onSelectPlayer = (player) => {
  showSelector.value = false
  emit('select-player', player)
}

const activeQueueId = ref(null)
const activePlayerId = ref(null)
const queueLabel = ref('Music Assistant')
const playState = ref('idle')
const trackName = ref('')
const artistName = ref('')
const artworkUrl = ref('')
const duration = ref(0)
const elapsed = ref(0)
const elapsedUpdatedAt = ref(0)
const volume = ref(0)
const shuffleOn = ref(false)
const repeatMode = ref('off')

const isDragging = ref(false)
const dragElapsed = ref(0)
const isVolDragging = ref(false)
const dragVolume = ref(0)

const maConnected = computed(() => !!props.maState?.connected)

const currentElapsed = computed(() => {
  if (isDragging.value) return dragElapsed.value
  if (playState.value !== 'playing') return elapsed.value
  const now = Date.now() / 1000
  const delta = now - elapsedUpdatedAt.value
  return Math.min(elapsed.value + delta, duration.value || Number.MAX_SAFE_INTEGER)
})

const progressPercent = computed(() => {
  if (duration.value <= 0) return 0
  return Math.max(0, Math.min(100, (currentElapsed.value / duration.value) * 100))
})

const displayedVolume = computed(() => {
  return isVolDragging.value ? dragVolume.value : volume.value
})

const pickActiveQueue = (queues = [], requestedQueueId = null) => {
  if (!Array.isArray(queues) || queues.length === 0) return null
  if (requestedQueueId) {
    const byId = queues.find((item) => item.queue_id === requestedQueueId)
    if (byId) return byId
  }
  return (
    queues.find((item) => ['playing', 'paused'].includes(item.state)) ||
    queues.find((item) => item.current_item) ||
    queues.find((item) => item.available) ||
    queues[0]
  )
}

const pickActivePlayer = (players = [], state = {}, queueId = null) => {
  if (!Array.isArray(players) || players.length === 0) return null
  const map = state.queue_player_map || {}

  if (state.active_player_id) {
    const byId = players.find((item) => item.player_id === state.active_player_id)
    if (byId) return byId
  }

  if (queueId && map[queueId]) {
    const mapped = players.find((item) => item.player_id === map[queueId])
    if (mapped) return mapped
  }

  if (queueId) {
    const byQueueId = players.find((item) => item.player_id === queueId)
    if (byQueueId) return byQueueId
  }

  return players.find((item) => ['playing', 'paused'].includes(item.playback_state)) || players[0]
}

const applyMAState = (state) => {
  const queues = state?.queues || []
  const players = state?.players || []

  const queue = pickActiveQueue(queues, state?.active_queue_id)
  const queueId = queue?.queue_id || null
  const player = pickActivePlayer(players, state || {}, queueId)

  activeQueueId.value = queueId
  activePlayerId.value = player?.player_id || null
  queueLabel.value = (queue?.display_name || player?.name || 'Music Assistant').slice(0, 18)

  playState.value = queue?.state || player?.playback_state || 'idle'
  shuffleOn.value = !!queue?.shuffle_enabled
  repeatMode.value = queue?.repeat_mode || 'off'

  duration.value = Number(queue?.current_item?.duration || queue?.current_item?.media_item?.duration || 0)
  elapsed.value = Number(queue?.elapsed_time || 0)
  elapsedUpdatedAt.value = Number(queue?.elapsed_time_last_updated || Date.now() / 1000)

  const currentItem = queue?.current_item
  if (currentItem) {
    trackName.value = currentItem.media_item?.name || currentItem.name || ''
    artistName.value = currentItem.media_item?.artists?.map((artist) => artist.name).join(', ') || ''
    const images = currentItem.media_item?.metadata?.images || []
    const thumb = images.find((image) => image.type === 'thumb') || images[0]
    const path = thumb?.path || ''
    if (path.startsWith('/')) {
      artworkUrl.value = `${state.ma_base_url}${path}`
    } else {
      artworkUrl.value = path
    }
  } else {
    trackName.value = ''
    artistName.value = ''
    artworkUrl.value = ''
  }

  const serverVolume = Number(player?.volume_level)
  if (Number.isFinite(serverVolume)) {
    volume.value = Math.max(0, Math.min(100, Math.round(serverVolume)))
    if (!isVolDragging.value) {
      dragVolume.value = volume.value
    }
  }
}

watch(
  () => props.maState,
  (state) => { applyMAState(state || {}) },
  { immediate: true, deep: true }
)

const formatTime = (seconds) => {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00'
  const total = Math.floor(seconds)
  const minutes = Math.floor(total / 60)
  const secs = total % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

const sendMACmd = async (command, args = {}) => {
  if (!maConnected.value) return
  try {
    const response = await fetch('/api/ma/cmd', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, args })
    })
    if (!response.ok) {
      const message = await response.text()
      throw new Error(message)
    }
  } catch (error) {
    console.error(`MA command failed: ${command}`, error)
  }
}

const togglePlay = () => {
  if (!activeQueueId.value) return
  sendMACmd('player_queues/play_pause', { queue_id: activeQueueId.value })
}

const nextTrack = () => {
  if (!activeQueueId.value) return
  sendMACmd('player_queues/next', { queue_id: activeQueueId.value })
}

const prevTrack = () => {
  if (!activeQueueId.value) return
  sendMACmd('player_queues/previous', { queue_id: activeQueueId.value })
}

const seekTo = (position) => {
  if (!activeQueueId.value) return
  const safePosition = Math.max(0, Math.floor(position))
  sendMACmd('player_queues/seek', { queue_id: activeQueueId.value, position: safePosition })
}

const setVolume = (value) => {
  if (!activePlayerId.value) return
  const safeVolume = Math.max(0, Math.min(100, Math.round(value)))
  volume.value = safeVolume
  dragVolume.value = safeVolume
  sendMACmd('players/cmd/volume_set', { player_id: activePlayerId.value, volume_level: safeVolume })
}

const computeProgressFromEvent = (event, targetElement) => {
  if (duration.value <= 0) return 0
  const rect = targetElement.getBoundingClientRect()
  const percent = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width))
  return percent * duration.value
}

const onProgressClick = (event) => {
  if (duration.value <= 0) return
  const position = computeProgressFromEvent(event, event.currentTarget)
  elapsed.value = position
  elapsedUpdatedAt.value = Date.now() / 1000
  seekTo(position)
}

const onProgressMouseDown = (event) => {
  if (duration.value <= 0) return
  isDragging.value = true
  dragElapsed.value = computeProgressFromEvent(event, event.currentTarget)
  document.addEventListener('mousemove', onProgressMouseMove)
  document.addEventListener('mouseup', onProgressMouseUp)
}

const onProgressMouseMove = (event) => {
  if (!isDragging.value) return
  const track = document.querySelector('.progress-bar-track')
  if (!track) return
  dragElapsed.value = computeProgressFromEvent(event, track)
}

const onProgressMouseUp = () => {
  if (!isDragging.value) return
  isDragging.value = false
  elapsed.value = dragElapsed.value
  elapsedUpdatedAt.value = Date.now() / 1000
  seekTo(dragElapsed.value)
  document.removeEventListener('mousemove', onProgressMouseMove)
  document.removeEventListener('mouseup', onProgressMouseUp)
}

const computeVolumeFromEvent = (event, targetElement) => {
  const rect = targetElement.getBoundingClientRect()
  const percent = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width))
  return Math.round(percent * 100)
}

const onVolumeClick = (event) => {
  const value = computeVolumeFromEvent(event, event.currentTarget)
  setVolume(value)
}

const onVolumeMouseDown = (event) => {
  isVolDragging.value = true
  dragVolume.value = computeVolumeFromEvent(event, event.currentTarget)
  document.addEventListener('mousemove', onVolumeMouseMove)
  document.addEventListener('mouseup', onVolumeMouseUp)
}

const onVolumeMouseMove = (event) => {
  if (!isVolDragging.value) return
  const track = document.querySelector('.volume-track')
  if (!track) return
  dragVolume.value = computeVolumeFromEvent(event, track)
}

const onVolumeMouseUp = () => {
  if (!isVolDragging.value) return
  isVolDragging.value = false
  setVolume(dragVolume.value)
  document.removeEventListener('mousemove', onVolumeMouseMove)
  document.removeEventListener('mouseup', onVolumeMouseUp)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onProgressMouseMove)
  document.removeEventListener('mouseup', onProgressMouseUp)
  document.removeEventListener('mousemove', onVolumeMouseMove)
  document.removeEventListener('mouseup', onVolumeMouseUp)
})
</script>
