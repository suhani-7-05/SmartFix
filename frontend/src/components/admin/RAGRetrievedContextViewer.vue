<script setup>
defineProps({
  ragData: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h3>RAG Vector Search & Retrieval</h3>
      <span v-if="ragData.retrieved_count !== undefined" class="card-sub">
        Retrieved {{ ragData.retrieved_count }} relevant manual chunks
      </span>
    </div>

    <div v-if="!ragData || !ragData.query" class="state-box">
      Run a troubleshooting query to inspect RAG query vector embedding and retrieved manual chunks.
    </div>

    <div v-else class="rag-content">
      <!-- Query Embedding Metadata -->
      <div v-if="ragData.query_embedding_metadata" class="embedding-bar">
        <div class="embed-meta">
          <span class="label">Query Vector Model:</span>
          <span class="val font-mono">{{ ragData.query_embedding_metadata.model }}</span>
        </div>
        <div class="embed-meta">
          <span class="label">Dimensions:</span>
          <span class="val font-mono">{{ ragData.query_embedding_metadata.dimensions }}</span>
        </div>
        <div class="embed-meta">
          <span class="label">Vector Sample:</span>
          <span class="val font-mono">
            [{{ ragData.query_embedding_metadata.vector_preview?.slice(0, 4).map(n => n.toFixed(3)).join(', ') }}...]
          </span>
        </div>
      </div>

      <!-- Top-K Retrieved Chunks Table -->
      <div class="chunks-section">
        <span class="section-title">Retrieved Chunks & Similarity Scores</span>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Source Document</th>
                <th>Vector ID</th>
                <th>Distance</th>
                <th>Similarity Score</th>
                <th>Matched Manual Chunk Snippet</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(chunk, idx) in ragData.retrieved_chunks" :key="idx">
                <td class="font-medium">{{ chunk.document_filename }}</td>
                <td><code class="font-mono">{{ chunk.vector_id }}</code></td>
                <td>{{ chunk.distance }}</td>
                <td>
                  <span class="score-badge" :class="{ high: chunk.similarity_score > 0.05 }">
                    {{ (chunk.similarity_score * 100).toFixed(1) }}%
                  </span>
                </td>
                <td class="snippet-cell">{{ chunk.text }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Constructed LLM Context Box -->
      <div class="context-section">
        <span class="section-title">Constructed Prompt Context Sent to Code Llama</span>
        <pre class="context-box">{{ ragData.constructed_context }}</pre>
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
  margin-bottom: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.card-sub {
  font-size: 0.78rem;
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

.rag-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.embedding-bar {
  display: flex;
  gap: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-light);
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.78rem;
}

.embed-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.label {
  color: var(--text-dim);
}

.val {
  color: var(--accent);
  font-weight: 500;
}

.font-mono {
  font-family: var(--font-mono);
}

.section-title {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
}

.table-wrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  text-align: left;
}

.table th {
  padding: 0.5rem 0.65rem;
  background: rgba(0, 0, 0, 0.25);
  color: var(--text-dim);
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.7rem;
}

.table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-muted);
  vertical-align: top;
}

.font-medium {
  font-weight: 500;
  color: var(--text-main);
}

.snippet-cell {
  max-width: 320px;
  white-space: pre-wrap;
  word-break: break-word;
}

.score-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.72rem;
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent);
}

.score-badge.high {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.context-box {
  margin: 0;
  padding: 0.75rem;
  background: #000000;
  border: 1px solid var(--border-light);
  border-radius: var(--radius);
  color: #d1d5db;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 220px;
  overflow-y: auto;
}
</style>
