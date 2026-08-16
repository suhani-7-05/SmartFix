<script setup>
defineProps({
  document: {
    type: Object,
    default: null,
  },
  chunks: {
    type: Array,
    default: () => [],
  },
  selectedChunkId: {
    type: String,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["select-chunk"]);
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h3>Extracted Chunks</h3>
      <span v-if="document" class="card-sub">{{ document.filename }} ({{ chunks.length }} chunks)</span>
    </div>

    <div v-if="loading" class="state-box">Loading chunks...</div>
    <div v-else-if="!document" class="state-box">Select a document above to view chunks.</div>
    <div v-else-if="chunks.length === 0" class="state-box">No chunks found.</div>

    <div v-else class="chunk-list">
      <div
        v-for="chunk in chunks"
        :key="chunk.id"
        class="chunk-item"
        :class="{ active: chunk.id === selectedChunkId }"
        @click="emit('select-chunk', chunk)"
      >
        <div class="chunk-meta">
          <span class="chunk-idx">Chunk #{{ chunk.chunk_index + 1 }}</span>
          <span class="char-range">Offset {{ chunk.char_start }}..{{ chunk.char_end }}</span>
        </div>

        <pre class="chunk-body">{{ chunk.text }}</pre>

        <div class="chunk-footer">
          <span>Vector ID: <code>{{ chunk.vector_id || 'N/A' }}</code></span>
          <button class="btn-link" @click.stop="emit('select-chunk', chunk)">View Embedding ➔</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.card-sub {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.state-box {
  padding: 2rem;
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-dim);
  background: rgba(0, 0, 0, 0.15);
  border-radius: var(--radius);
}

.chunk-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 440px;
  overflow-y: auto;
}

.chunk-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 0.85rem;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.chunk-item:hover {
  border-color: rgba(59, 130, 246, 0.3);
}

.chunk-item.active {
  border-color: var(--accent);
  background: var(--accent-light);
}

.chunk-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
}

.chunk-idx {
  font-weight: 600;
  color: var(--text-main);
}

.char-range {
  color: var(--text-dim);
  font-family: var(--font-mono);
}

.chunk-body {
  margin: 0 0 0.5rem 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.45;
}

.chunk-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.72rem;
  color: var(--text-dim);
}

.chunk-footer code {
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.btn-link {
  background: transparent;
  border: none;
  color: var(--accent);
  cursor: pointer;
  padding: 0;
  font-size: 0.72rem;
}

.btn-link:hover {
  text-decoration: underline;
}
</style>
