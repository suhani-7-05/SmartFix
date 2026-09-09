<script setup>
import { ref } from "vue";
import { CATEGORY_SAMPLE_QUESTIONS } from "../../constants/models.js";

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false,
  },
  compareData: {
    type: Object,
    default: () => ({
      models: {},
      safety_decision: "ALLOWED",
      equipment_id: "N/A",
      total_duration_ms: 0,
    }),
  },
  errorMessage: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["submit-compare"]);

const questionText = ref("What does the search_similar() function in vector_store.py do?");
const activeCategoryFilter = ref("Explanation");

function submit() {
  if (!questionText.value.trim() || props.isLoading) return;
  emit("submit-compare", questionText.value.trim());
}

function selectSample(sample) {
  questionText.value = sample.question;
  activeCategoryFilter.value = sample.category;
  submit();
}

function onKeydown(e) {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    submit();
  }
}
</script>

<template>
  <div class="compare-container">
    <!-- Header Section -->
    <div class="compare-header">
      <div class="header-titles">
        <span class="badge-tag">Multi-Model Real-Time Evaluation</span>
        <h3>Side-by-Side Model Comparison (Ollama)</h3>
        <p>Send identical prompts to Code Llama (7B), StarCoder2 (3B), and Qwen 2.5 Coder (1.5B) to evaluate latency, code generation, and diagnostic accuracy side-by-side.</p>
      </div>
    </div>

    <!-- Category Preset Chips -->
    <div class="category-preset-section">
      <span class="preset-label">7 Software Engineering Categories:</span>
      <div class="preset-chips">
        <button
          v-for="sample in CATEGORY_SAMPLE_QUESTIONS"
          :key="sample.category"
          type="button"
          class="cat-chip"
          :class="{ active: activeCategoryFilter === sample.category }"
          :disabled="isLoading"
          @click="selectSample(sample)"
        >
          <span class="chip-dot"></span>
          <span class="chip-name">{{ sample.category }}</span>
        </button>
      </div>
    </div>

    <!-- Question Input Box -->
    <div class="input-card">
      <div class="input-header">
        <label for="compare-query-input">Troubleshooting or Codebase Query</label>
        <span class="shortcut-hint">Ctrl + Enter to run all 3 models</span>
      </div>
      <textarea
        id="compare-query-input"
        v-model="questionText"
        rows="3"
        class="compare-textarea"
        placeholder="Enter a troubleshooting question, codebase inquiry, or code generation task..."
        :disabled="isLoading"
        @keydown="onKeydown"
      ></textarea>
      <div class="input-actions">
        <div v-if="compareData.safety_decision" class="safety-indicator">
          <span class="indicator-label">Safety Status:</span>
          <span :class="['safety-pill', compareData.safety_decision.toLowerCase()]">
            {{ compareData.safety_decision }}
          </span>
          <span v-if="compareData.equipment_id" class="eq-pill">
            EQ: {{ compareData.equipment_id }}
          </span>
        </div>
        <button
          type="button"
          class="run-compare-btn"
          :disabled="isLoading || !questionText.trim()"
          @click="submit"
        >
          <span v-if="isLoading" class="btn-spinner"></span>
          <span>{{ isLoading ? "Querying 3 Models..." : "Run Multi-Model Comparison" }}</span>
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="errorMessage" class="error-banner">
      <strong>Error:</strong> {{ errorMessage }}
    </div>

    <!-- Loading State Preview -->
    <div v-if="isLoading" class="evaluating-overlay">
      <div class="spinner-pulse"></div>
      <h4>Executing local Ollama inference across all 3 models...</h4>
      <p>Benchmarking Code Llama (7B), StarCoder2 (3B), and Qwen 2.5 Coder (1.5B) under identical parameters ($T=0.2$).</p>
    </div>

    <!-- 3-Column Side-by-Side Model Results -->
    <div v-if="!isLoading && compareData.models && Object.keys(compareData.models).length > 0" class="models-grid">
      <!-- Qwen 2.5 Coder Card -->
      <div class="model-card qwen-card">
        <div class="model-card-header">
          <div class="model-meta">
            <div class="model-badge-circle qwen-bg">Q</div>
            <div>
              <h4>Qwen 2.5 Coder</h4>
              <span class="param-tag">1.5B Parameters • Ultra-Fast</span>
            </div>
          </div>
          <div class="latency-badge" v-if="compareData.models['qwen2.5-coder']">
            ⏱️ {{ (compareData.models['qwen2.5-coder'].latency_ms / 1000).toFixed(2) }}s
          </div>
        </div>
        <div class="model-card-body">
          <div class="stats-row" v-if="compareData.models['qwen2.5-coder']">
            <span>Tokens: <strong>{{ compareData.models['qwen2.5-coder'].eval_count || 'N/A' }}</strong></span>
            <span>Speed: <strong>{{ ((compareData.models['qwen2.5-coder'].eval_count || 0) / ((compareData.models['qwen2.5-coder'].latency_ms || 1) / 1000)).toFixed(1) }} tok/s</strong></span>
          </div>
          <div class="response-content">
            <pre>{{ compareData.models['qwen2.5-coder']?.answer || "No response generated." }}</pre>
          </div>
        </div>
      </div>

      <!-- StarCoder2 Card -->
      <div class="model-card starcoder-card">
        <div class="model-card-header">
          <div class="model-meta">
            <div class="model-badge-circle starcoder-bg">S</div>
            <div>
              <h4>StarCoder2</h4>
              <span class="param-tag">3B Parameters • Code & Refactor</span>
            </div>
          </div>
          <div class="latency-badge" v-if="compareData.models['starcoder2']">
            ⏱️ {{ (compareData.models['starcoder2'].latency_ms / 1000).toFixed(2) }}s
          </div>
        </div>
        <div class="model-card-body">
          <div class="stats-row" v-if="compareData.models['starcoder2']">
            <span>Tokens: <strong>{{ compareData.models['starcoder2'].eval_count || 'N/A' }}</strong></span>
            <span>Speed: <strong>{{ ((compareData.models['starcoder2'].eval_count || 0) / ((compareData.models['starcoder2'].latency_ms || 1) / 1000)).toFixed(1) }} tok/s</strong></span>
          </div>
          <div class="response-content">
            <pre>{{ compareData.models['starcoder2']?.answer || "No response generated." }}</pre>
          </div>
        </div>
      </div>

      <!-- Code Llama Card -->
      <div class="model-card codellama-card">
        <div class="model-card-header">
          <div class="model-meta">
            <div class="model-badge-circle codellama-bg">C</div>
            <div>
              <h4>Code Llama</h4>
              <span class="param-tag">7B Parameters • Deep Reasoning</span>
            </div>
          </div>
          <div class="latency-badge" v-if="compareData.models['codellama']">
            ⏱️ {{ (compareData.models['codellama'].latency_ms / 1000).toFixed(2) }}s
          </div>
        </div>
        <div class="model-card-body">
          <div class="stats-row" v-if="compareData.models['codellama']">
            <span>Tokens: <strong>{{ compareData.models['codellama'].eval_count || 'N/A' }}</strong></span>
            <span>Speed: <strong>{{ ((compareData.models['codellama'].eval_count || 0) / ((compareData.models['codellama'].latency_ms || 1) / 1000)).toFixed(1) }} tok/s</strong></span>
          </div>
          <div class="response-content">
            <pre>{{ compareData.models['codellama']?.answer || "No response generated." }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.compare-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.compare-header {
  background: var(--surface-bg, #1a202c);
  border: 1px solid var(--border-color, #2d3748);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
}

.badge-tag {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  margin-bottom: 0.5rem;
}

.header-titles h3 {
  margin: 0 0 0.4rem 0;
  font-size: 1.3rem;
  color: #f7fafc;
}

.header-titles p {
  margin: 0;
  font-size: 0.88rem;
  color: #a0aec0;
  line-height: 1.45;
}

.category-preset-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preset-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.preset-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.cat-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #232d3d;
  border: 1px solid #3b485d;
  color: #e2e8f0;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-chip:hover {
  background: #2d3b50;
  border-color: #6366f1;
}

.cat-chip.active {
  background: #4f46e5;
  border-color: #818cf8;
  color: #ffffff;
  font-weight: 600;
}

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #38bdf8;
}

.cat-chip.active .chip-dot {
  background: #ffffff;
}

.input-card {
  background: #1a202c;
  border: 1px solid #2d3748;
  border-radius: 10px;
  padding: 1.25rem;
}

.input-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.input-header label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
}

.shortcut-hint {
  font-size: 0.75rem;
  color: #718096;
}

.compare-textarea {
  width: 100%;
  box-sizing: border-box;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #f8fafc;
  padding: 0.75rem;
  font-family: inherit;
  font-size: 0.92rem;
  resize: vertical;
}

.compare-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}

.safety-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #94a3b8;
}

.safety-pill {
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.safety-pill.allowed {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.safety-pill.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.safety-pill.blocked {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.eq-pill {
  background: #334155;
  color: #cbd5e1;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.run-compare-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #fff;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.run-compare-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.run-compare-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.evaluating-overlay {
  text-align: center;
  padding: 3rem 1rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
}

.spinner-pulse {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.25rem;
}

.evaluating-overlay h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.15rem;
  color: #f1f5f9;
}

.evaluating-overlay p {
  margin: 0;
  font-size: 0.88rem;
  color: #94a3b8;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

@media (max-width: 1100px) {
  .models-grid {
    grid-template-columns: 1fr;
  }
}

.model-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.qwen-card {
  border-top: 4px solid #10b981;
}

.starcoder-card {
  border-top: 4px solid #3b82f6;
}

.codellama-card {
  border-top: 4px solid #8b5cf6;
}

.model-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: #162032;
  border-bottom: 1px solid #273549;
}

.model-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.model-badge-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: #fff;
}

.qwen-bg { background: #10b981; }
.starcoder-bg { background: #3b82f6; }
.codellama-bg { background: #8b5cf6; }

.model-meta h4 {
  margin: 0;
  font-size: 0.95rem;
  color: #f8fafc;
}

.param-tag {
  font-size: 0.75rem;
  color: #94a3b8;
}

.latency-badge {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid #334155;
  color: #f1f5f9;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.model-card-body {
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #94a3b8;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed #334155;
}

.response-content {
  flex: 1;
  max-height: 420px;
  overflow-y: auto;
}

.response-content pre {
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.82rem;
  line-height: 1.5;
  color: #e2e8f0;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-banner {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
}
</style>
