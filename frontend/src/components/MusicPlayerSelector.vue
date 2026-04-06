<template>
  <div class="relative">
    <button
      class="flex items-center gap-1 px-2 py-0.5 rounded border text-xs transition-colors"
      :class="activePlayer ? 'border-purple-500/40 text-purple-300 hover:bg-purple-500/10' : 'border-white/10 text-white/40 hover:border-white/20'"
      @click="show = !show"
    >
      {{ activePlayer ? (activePlayer.friendly_name || activePlayer.name || shortId(activePlayer.player_id)) : '选择播放器' }}
      <span class="text-white/30">▼</span>
    </button>

    <div v-if="show" class="absolute right-0 top-full mt-1 z-30 glass-effect rounded-lg border border-white/10 py-1 min-w-[140px]">
      <div
        v-for="player in players" :key="player.player_id"
        class="px-3 py-1.5 text-xs cursor-pointer hover:bg-white/10 transition-colors"
        :class="currentPlayerId === player.player_id ? 'text-purple-300 bg-purple-500/10' : 'text-white/60'"
        @click="selectPlayer(player)"
      >
        {{ player.friendly_name || player.name || shortId(player.player_id) }}
      </div>
      <div v-if="!players.length" class="px-3 py-1.5 text-xs text-white/30">无可用播放器</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  maState: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['select-player'])

const show = ref(false)

const players = computed(() => props.maState.players || [])
const currentPlayerId = computed(() => props.maState.active_player_id || null)
const activePlayer = computed(() =>
  players.value.find(p => p.player_id === currentPlayerId.value) || null
)

const shortId = (id) => String(id).slice(-8)

const selectPlayer = (player) => {
  show.value = false
  emit('select-player', player)
}
</script>

<style scoped>
.glass-effect {
  background: rgba(20, 20, 40, 0.85);
  backdrop-filter: blur(8px);
}
</style>
