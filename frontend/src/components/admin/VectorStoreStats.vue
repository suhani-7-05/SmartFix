<script setup>
defineProps({
  stats: {
    type: Object,
    default: () => ({
      documents: 0,
      chunks: 0,
      embedded_chunks: 0,
      vector_store: {
        collection: "smartfix_chunks",
        vector_count: 0,
      },
    }),
  },
  loading: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div class="stats-bar">
    <div class="stat-item">
      <span class="stat-label">Documents</span>
      <span class="stat-value">{{ loading ? '-' : stats.documents }}</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-label">Extracted Chunks</span>
      <span class="stat-value">{{ loading ? '-' : stats.chunks }}</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-label">Embeddings</span>
      <span class="stat-value">{{ loading ? '-' : stats.embedded_chunks }}</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-label">ChromaDB Vectors</span>
      <span class="stat-value text-accent">{{ loading ? '-' : stats.vector_store?.vector_count || 0 }}</span>
    </div>
  </div>
</template>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1rem 1.5rem;
  margin-bottom: 1.25rem;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-value {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-main);
}

.text-accent {
  color: var(--accent);
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: var(--border-light);
}

@media (max-width: 640px) {
  .stats-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .stat-divider {
    display: none;
  }
}
</style>
