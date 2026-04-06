<template>
  <div class="p-2 flex-1 flex flex-col min-h-0">
    <div class="glass-panel rounded-[2rem] p-5 card-hover flex-1 flex flex-col min-h-0 relative overflow-hidden group">
      
      <!-- 动态氛围背光 -->
      <div v-if="playState === 'playing'" 
        class="absolute -top-20 -right-20 w-64 h-64 bg-cyan-500/10 blur-[100px] rounded-full animate-pulse transition-all duration-1000"></div>
      <div v-if="playState === 'playing'" 
        class="absolute -bottom-20 -left-20 w-64 h-64 bg-purple-500/10 blur-[100px] rounded-full animate-pulse transition-all duration-1000 delay-700"></div>

      <div class="flex items-center gap-2.5 mb-5 relative z-10">
        <div class="w-2.5 h-2.5 rounded-full ring-4 ring-black/20" :class="maConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'"></div>
        <span class="text-[10px] font-extrabold tracking-[0.2em] uppercase font-heading" :class="maConnected ? 'text-emerald-400/80' : 'text-red-400/70'">
          {{ maConnected ? 'MA ONLINE' : 'MA OFFLINE' }}
        </span>
        <div class="flex-1"></div>
        <span class="text-[10px] text-white/20 font-bold uppercase tracking-widest truncate max-w-[120px]">{{ queueLabel }}</span>
      </div>
 
      <!-- 封面艺术 -->
      <div class="aspect-square rounded-[1.5rem] overflow-hidden mb-6 relative group/cover shadow-2xl ring-1 ring-white/10 bg-black/40">
        <img
          :src="artworkUrl || fallbackArtwork"
          alt="Cover"
          class="w-full h-full object-cover transition-transform duration-700 group-hover/cover:scale-110"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60"></div>
 
        <div v-if="playState === 'playing'" class="absolute bottom-4 right-4 w-10 h-10 bg-white/10 backdrop-blur-xl rounded-2xl flex items-center justify-center border border-white/20 shadow-xl">
          <div class="flex gap-[3px] items-end pb-1">
            <span class="w-[3px] h-3 bg-cyan-400 rounded-full animate-[music-bar_0.8s_ease-in-out_infinite]"></span>
            <span class="w-[3px] h-5 bg-cyan-400 rounded-full animate-[music-bar_0.8s_ease-in-out_0.2s_infinite]"></span>
            <span class="w-[3px] h-4 bg-cyan-400 rounded-full animate-[music-bar_0.8s_ease-in-out_0.4s_infinite]"></span>
          </div>
        </div>
      </div>
 
      <!-- 曲目信息 -->
      <div class="text-center mb-6 relative z-10 px-2">
        <h3 class="font-extrabold text-lg leading-tight text-white mb-1 font-heading truncate">{{ trackName || 'CHILLING...' }}</h3>
        <p class="text-sm font-medium text-cyan-400/80 truncate tracking-wide opacity-80">{{ artistName || 'Music Assistant' }}</p>
      </div>
 
      <!-- 进度条 -->
      <div class="mb-6 px-1">
        <div
          class="progress-bar-track w-full h-2.5 bg-white/5 rounded-full cursor-pointer group/bar relative overflow-hidden"
          @click="onProgressClick"
          @mousedown.prevent="onProgressMouseDown"
        >
          <div
            class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full relative shadow-[0_0_15px_rgba(34,211,238,0.4)]"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
        <div class="flex justify-between mt-2 px-1">
          <span class="text-[10px] font-bold text-white/30 tabular-nums">{{ formatTime(currentElapsed) }}</span>
          <span class="text-[10px] font-bold text-white/30 tabular-nums">{{ formatTime(duration) }}</span>
        </div>
      </div>
 
      <!-- 主控制器 -->
      <div class="flex items-center justify-between gap-2 px-2 pb-2 mt-auto">
        <button class="p-3 text-white/30 hover:text-white transition-all transform active:scale-90" :disabled="!activeQueueId" @click="toggleShuffle">
          <svg class="w-5 h-5" :class="shuffleOn ? 'text-cyan-400 glow-blue' : ''" fill="currentColor" viewBox="0 0 24 24"><path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/></svg>
        </button>
        
        <div class="flex items-center gap-4">
          <button class="p-3 text-white/40 hover:text-white transition-all active:scale-90" :disabled="!activeQueueId" @click="prevTrack">
            <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>
          
          <button class="w-14 h-14 flex items-center justify-center bg-white text-black rounded-2xl shadow-[0_10px_20px_rgba(255,255,255,0.1)] transition-all hover:scale-105 active:scale-95 disabled:opacity-40" 
            :disabled="!activeQueueId" @click="togglePlay">
            <svg v-if="playState === 'playing'" class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
            <svg v-else class="w-8 h-8 translate-x-[1px]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
          
          <button class="p-3 text-white/40 hover:text-white transition-all active:scale-90" :disabled="!activeQueueId" @click="nextTrack">
            <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>
        </div>

        <button class="p-3 text-white/30 hover:text-white transition-all transform active:scale-90 relative" :disabled="!activeQueueId" @click="cycleRepeat">
          <svg class="w-5 h-5" :class="repeatMode !== 'off' ? 'text-cyan-400 glow-blue' : ''" fill="currentColor" viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/></svg>
          <span v-if="repeatMode === 'one'" class="absolute top-2 right-2 text-[8px] font-black text-cyan-400">1</span>
        </button>
      </div>
 
      <!-- 音量控制 -->
      <div class="flex items-center gap-4 mt-6 bg-white/5 p-3 rounded-2xl border border-white/5">
        <svg class="w-4 h-4 text-white/30 shrink-0" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 9v6h4l5 5V4L7 9H3z"/>
        </svg>
        <div
          class="volume-track relative flex-1 h-2 bg-white/10 rounded-full cursor-pointer transition-all"
          @click="onVolumeClick"
          @mousedown.prevent="onVolumeMouseDown"
        >
          <div class="h-full bg-white/50 rounded-full" :style="{ width: displayedVolume + '%' }"></div>
        </div>
        <span class="text-[10px] font-black text-white/40 w-8 text-right font-heading">{{ displayedVolume }}</span>
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
