<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  chunk: {
    type: Object,
    default: null,
  },
  vectorData: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const showRawJson = ref(false);

const vectorPreview = computed(() => {
  if (!props.vectorData || !props.vectorData.embedding_preview) return [];
  return props.vectorData.embedding_preview;
});
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h3>Vector Metadata</h3>
      <button v-if="vectorData" class="btn-toggle" @click="showRawJson = !showRawJson">
        {{ showRawJson ? 'Formatted' : 'Raw JSON' }}
      </button>
    </div>

    <div v-if="loading" class="state-box">Loading vector from ChromaDB...</div>
    <div v-else-if="!chunk" class="state-box">Select a chunk to view embedding data.</div>
    <div v-else-if="!vectorData" class="state-box">Vector metadata unavailable.</div>

    <div v-else-if="showRawJson" class="raw-json">
      <pre>{{ JSON.stringify(vectorData, null, 2) }}</pre>
    </div>

    <div v-else class="vector-content">
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">Vector ID</span>
          <span class="info-val font-mono">{{ vectorData.vector_id }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Model</span>
          <span class="info-val">{{ chunk.embedding_model || 'nomic-embed-text' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Dimensions</span>
          <span class="info-val">{{ vectorData.dimensions || 384 }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Distance Metric</span>
          <span class="info-val">Cosine</span>
        </div>
      </div>

      <div class="section-box">
        <span class="info-label">Embedding Vector (Sample Float Array)</span>
        <div class="float-list">
          <span v-for="(val, idx) in vectorPreview" :key="idx" class="float-tag">
            {{ typeof val === 'number' ? val.toFixed(5) : val }}
          </span>
        </div>
      </div>

      <div class="section-box">
        <span class="info-label">Stored Chunk Content</span>
        <div class="stored-text">{{ vectorData.text }}</div>
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
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.btn-toggle {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-toggle:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
}

.state-box {
  padding: 2rem;
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-dim);
  background: rgba(0, 0, 0, 0.15);
  border-radius: var(--radius);
}

.vector-content {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.info-label {
  font-size: 0.7rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-val {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-main);
}

.font-mono {
  font-family: var(--font-mono);
  color: var(--accent);
}

.section-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.float-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.float-tag {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-light);
  color: var(--accent);
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
}

.stored-text {
  font-size: 0.8rem;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-light);
  padding: 0.65rem;
  border-radius: 4px;
  line-height: 1.4;
}

.raw-json pre {
  margin: 0;
  background: #000000;
  padding: 0.75rem;
  border-radius: 4px;
  color: #a7f3d0;
  font-size: 0.75rem;
  overflow-x: auto;
  max-height: 350px;
}
</style>
