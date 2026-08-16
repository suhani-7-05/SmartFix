<script setup>
import { ref } from "vue";

const props = defineProps({
  documents: {
    type: Array,
    default: () => [],
  },
  selectedDocId: {
    type: String,
    default: null,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
  uploadError: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["upload", "select-doc", "delete-doc"]);

const fileInputRef = ref(null);
const dragOver = ref(false);

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    emit("upload", file);
    if (fileInputRef.value) fileInputRef.value.value = "";
  }
}

function handleDrop(event) {
  dragOver.value = false;
  const file = event.dataTransfer.files[0];
  if (file) {
    emit("upload", file);
  }
}

function formatDate(isoStr) {
  if (!isoStr) return "-";
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return isoStr;
  }
}
</script>

<template>
  <div class="card">
    <div class="card-title-row">
      <h3>Documents</h3>
      <span class="card-sub">Upload plain text (.txt), Markdown (.md), or PDF (.pdf)</span>
    </div>

    <!-- Upload Box -->
    <div
      class="upload-box"
      :class="{ 'drag-over': dragOver, uploading }"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="handleDrop"
      @click="fileInputRef && fileInputRef.click()"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".txt,.md,.pdf"
        class="hidden-input"
        @change="handleFileChange"
      />
      <div v-if="uploading" class="upload-text">
        <span class="spinner"></span>
        <span>Processing document (Extracting text ➔ Chunking ➔ Embedding ➔ ChromaDB)...</span>
      </div>
      <div v-else class="upload-text">
        <span>Click or drag a document file to upload</span>
      </div>
    </div>

    <div v-if="uploadError" class="error-msg">
      <span>{{ uploadError }}</span>
    </div>

    <!-- Documents Table -->
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Type</th>
            <th>Status</th>
            <th>Chars</th>
            <th>Chunks</th>
            <th>Uploaded</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="documents.length === 0">
            <td colspan="7" class="empty-cell">No documents uploaded yet.</td>
          </tr>
          <tr
            v-for="doc in documents"
            :key="doc.id"
            :class="{ active: doc.id === selectedDocId }"
            class="table-row"
            @click="emit('select-doc', doc.id)"
          >
            <td class="font-medium">{{ doc.filename }}</td>
            <td><span class="type-tag">{{ doc.file_type }}</span></td>
            <td>
              <span class="status-badge" :class="doc.status">
                {{ doc.status }}
              </span>
            </td>
            <td>{{ doc.extracted_text_length || '-' }}</td>
            <td><strong>{{ doc.chunk_count || 0 }}</strong></td>
            <td class="text-muted">{{ formatDate(doc.created_at) }}</td>
            <td class="text-right" @click.stop>
              <button
                class="btn-btn sm"
                :class="{ primary: doc.id === selectedDocId }"
                @click="emit('select-doc', doc.id)"
              >
                Inspect
              </button>
              <button class="btn-btn sm danger" @click="emit('delete-doc', doc.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
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

.card-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.card-title-row h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.card-sub {
  font-size: 0.78rem;
  color: var(--text-dim);
}

.upload-box {
  border: 1px dashed var(--border-color);
  border-radius: var(--radius);
  padding: 1rem;
  text-align: center;
  background: var(--bg-input);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
  margin-bottom: 1rem;
}

.upload-box:hover,
.upload-box.drag-over {
  border-color: var(--accent);
  background: var(--accent-light);
}

.upload-box.uploading {
  cursor: wait;
}

.hidden-input {
  display: none;
}

.upload-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.error-msg {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: var(--error);
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

.table-wrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  text-align: left;
}

.table th {
  padding: 0.6rem 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  color: var(--text-dim);
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  text-transform: uppercase;
  font-size: 0.7rem;
}

.table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-muted);
}

.table-row {
  cursor: pointer;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.table-row.active {
  background: var(--accent-light);
}

.font-medium {
  font-weight: 500;
  color: var(--text-main);
}

.type-tag {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-dim);
}

.status-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.processed {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}

.text-muted {
  color: var(--text-dim);
}

.text-right {
  text-align: right;
}

.empty-cell {
  text-align: center;
  padding: 1.5rem !important;
  color: var(--text-dim);
}

.btn-btn {
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-muted);
  font-size: 0.75rem;
  cursor: pointer;
  margin-left: 0.35rem;
  transition: all 0.15s ease;
}

.btn-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-main);
}

.btn-btn.primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

.btn-btn.danger:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: var(--error);
  color: var(--error);
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
