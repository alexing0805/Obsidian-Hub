<template>
  <div class="p-1 flex-1 flex flex-col min-h-0">
    <div class="glass-panel rounded-[1.5rem] p-3 card-hover flex flex-col min-h-0 relative overflow-hidden group">
      
      <!-- 1. 顶部：播放器选择 + 状态 -->
      <div class="flex items-center justify-between gap-2 mb-2 relative z-10 shrink-0">
        <div class="relative flex-1">
          <button 
            class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-left w-full group/btn"
            @click="showSelector = !showSelector"
          >
            <div class="w-1.5 h-1.5 rounded-full" :class="maConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'"></div>
            <span class="text-[10px] font-black text-white/60 uppercase tracking-tighter truncate flex-1">
              {{ activePlayerName || 'Select Player' }}
            </span>
            <span class="text-[8px] text-white/20 group-hover/btn:text-white/40">▼</span>
          </button>
          
          <!-- 内置选择器下拉 -->
          <div v-if="showSelector" class="absolute left-0 top-full mt-1 w-full z-50 bg-neutral-900/95 backdrop-blur-2xl rounded-xl border border-white/10 shadow-2xl py-1 max-h-[200px] overflow-y-auto animate-fade-in">
            <div 
              v-for="p in maState.players || []" :key="p.player_id"
              class="px-3 py-2 text-[10px] font-bold cursor-pointer hover:bg-white/10 transition-colors"
              :class="maState.active_player_id === p.player_id ? 'text-cyan-400 bg-cyan-400/10' : 'text-white/60'"
              @click="onSelectPlayer(p)"
            >
              {{ p.friendly_name || p.name }}
            </div>
            <div v-if="!(maState.players || []).length" class="px-3 py-2 text-[10px] text-white/30 italic">No players</div>
          </div>
        </div>
        <span class="text-[8px] text-white/10 font-bold uppercase tracking-widest truncate max-w-[60px]">{{ queueLabel }}</span>
      </div>
 
      <!-- 2. 中间：曲目信息 (横向展示) -->
      <div class="flex items-center gap-3 mb-3 shrink-0 px-1">
        <div class="w-10 h-10 rounded-lg overflow-hidden relative shadow-md ring-1 ring-white/10 bg-black/40 shrink-0">
          <img :src="artworkUrl || fallbackArtwork" alt="Cover" class="w-full h-full object-cover" />
          <div v-if="playState === 'playing'" class="absolute inset-0 bg-black/30 flex items-center justify-center">
             <div class="flex gap-[1px] items-end pb-0.5">
               <span class="w-[1.5px] h-1.5 bg-cyan-400 animate-[music-bar_0.8s_infinite]"></span>
               <span class="w-[1.5px] h-2.5 bg-cyan-400 animate-[music-bar_0.8s_0.2s_infinite]"></span>
               <span class="w-[1.5px] h-1.5 bg-cyan-400 animate-[music-bar_0.8s_0.4s_infinite]"></span>
             </div>
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-bold text-[11px] leading-tight text-white truncate font-heading">{{ trackName || 'Ready' }}</h3>
          <p class="text-[9px] font-medium text-cyan-400/50 truncate tracking-wide">{{ artistName || 'Music Assistant' }}</p>
        </div>
      </div>
 
      <!-- 3. 控制与进度 (紧凑集成) -->
      <div class="space-y-2 mt-auto">
        <div class="flex items-center gap-3 px-1">
          <div class="progress-bar-track flex-1 h-1 bg-white/5 rounded-full cursor-pointer relative" @click="onProgressClick" @mousedown.prevent="onProgressMouseDown">
            <div class="h-full bg-cyan-400 rounded-full" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <span class="text-[8px] font-black text-white/20 tabular-nums w-8 text-right">{{ formatTime(currentElapsed) }}</span>
        </div>

        <div class="flex items-center justify-between px-1">
          <div class="flex items-center gap-2">
            <button class="p-1 text-white/20 hover:text-white transition-all active:scale-75" :disabled="!activeQueueId" @click="prevTrack">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
            </button>
            <button class="w-8 h-8 flex items-center justify-center bg-white text-black rounded-lg shadow-sm transition-all active:scale-90" :disabled="!activeQueueId" @click="togglePlay">
              <svg v-if="playState === 'playing'" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
              <svg v-else class="w-4 h-4 translate-x-[1px]" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <button class="p-1 text-white/20 hover:text-white transition-all active:scale-75" :disabled="!activeQueueId" @click="nextTrack">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
            </button>
          </div>

          <div class="flex-1 max-w-[80px] flex items-center gap-2 bg-black/10 px-2 py-1 rounded-md border border-white/5">
            <svg class="w-2.5 h-2.5 text-white/20" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3z"/></svg>
            <div class="volume-track relative flex-1 h-0.5 bg-white/5 rounded-full cursor-pointer" @click="onVolumeClick" @mousedown.prevent="onVolumeMouseDown">
              <div class="h-full bg-white/20 rounded-full" :style="{ width: displayedVolume + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  maState: {
    type: Object,
    default: () => ({})
  }
})

const fallbackArtwork =
  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cmVjdCBmaWxsPSIjMWUyOTNiIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNGI1NTYzIiBmb250LXNpemU9IjQwIj7imao8L3RleHQ+PC9zdmc+'
 
const emit = defineEmits(['select-player'])

const showSelector = ref(false)
const activePlayerName = computed(() => {
  if (!props.maState?.active_player_id) return 'Select Player'
  const p = (props.maState.players || []).find(p => p.player_id === props.maState.active_player_id)
  return p ? (p.friendly_name || p.name) : 'Select Player'
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
  queueLabel.value = queue?.display_name || player?.name || 'Music Assistant'

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
  (state) => {
    applyMAState(state || {})
  },
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
  sendMACmd('player_queues/seek', {
    queue_id: activeQueueId.value,
    position: safePosition
  })
}

const setVolume = (value) => {
  if (!activePlayerId.value) return
  const safeVolume = Math.max(0, Math.min(100, Math.round(value)))
  volume.value = safeVolume
  dragVolume.value = safeVolume
  sendMACmd('players/cmd/volume_set', {
    player_id: activePlayerId.value,
    volume_level: safeVolume
  })
}

const toggleShuffle = () => {
  if (!activeQueueId.value) return
  const next = !shuffleOn.value
  shuffleOn.value = next
  sendMACmd('player_queues/shuffle', {
    queue_id: activeQueueId.value,
    shuffle_enabled: next
  })
}

const cycleRepeat = () => {
  if (!activeQueueId.value) return
  const modes = ['off', 'all', 'one']
  const index = modes.indexOf(repeatMode.value)
  const next = modes[(index + 1) % modes.length]
  repeatMode.value = next
  sendMACmd('player_queues/repeat', {
    queue_id: activeQueueId.value,
    repeat_mode: next
  })
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
