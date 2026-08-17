<script setup>
import { ref } from "vue";

const props = defineProps({
  trace: {
    type: Array,
    default: () => [],
  },
  totalDurationMs: {
    type: Number,
    default: 0,
  },
});

const expandedStep = ref(null);

function toggleStep(idx) {
  expandedStep.value = expandedStep.value === idx ? null : idx;
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div>
        <h3>Real Execution Trace</h3>
        <span class="card-sub">Orchestrator step-by-step REST service calls (Total time: {{ totalDurationMs }} ms)</span>
      </div>
    </div>

    <div v-if="trace.length === 0" class="state-box">
      Submit a question to trigger the Orchestrator and observe real service calls.
    </div>

    <div v-else class="trace-list">
      <div
        v-for="(step, idx) in trace"
        :key="idx"
        class="trace-step"
        :class="{ active: expandedStep === idx, error: step.status === 'ERROR' }"
      >
        <div class="step-summary" @click="toggleStep(idx)">
          <span class="step-num">Step {{ idx + 1 }}</span>
          <span class="step-name">{{ step.step_name }}</span>
          <span class="step-url font-mono">{{ step.method }} {{ step.url }}</span>

          <span class="step-duration font-mono">{{ step.duration_ms }} ms</span>
          <span class="step-status" :class="step.status.toLowerCase()">
            HTTP {{ step.http_code || 200 }}
          </span>

          <span class="toggle-icon">{{ expandedStep === idx ? '▲' : '▼' }}</span>
        </div>

        <div v-if="expandedStep === idx" class="step-details">
          <div class="detail-block">
            <span class="detail-label">Service Request Input Payload</span>
            <pre class="json-code">{{ JSON.stringify(step.input, null, 2) }}</pre>
          </div>

          <div class="detail-block">
            <span class="detail-label">Service Response Output Payload</span>
            <pre class="json-code">{{ JSON.stringify(step.output, null, 2) }}</pre>
          </div>

          <div v-if="step.error" class="error-box">
            <strong>Service Call Failure:</strong>
            <span>{{ step.error }}</span>
          </div>
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

.trace-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.trace-step {
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: border-color 0.15s ease;
}

.trace-step:hover {
  border-color: rgba(59, 130, 246, 0.4);
}

.trace-step.active {
  border-color: var(--accent);
  background: var(--accent-light);
}

.trace-step.error {
  border-color: var(--error);
}

.step-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  cursor: pointer;
  font-size: 0.82rem;
}

.step-num {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  color: var(--text-muted);
}

.step-name {
  font-weight: 600;
  color: var(--text-main);
  min-width: 140px;
}

.step-url {
  font-size: 0.75rem;
  color: var(--text-dim);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.font-mono {
  font-family: var(--font-mono);
}

.step-duration {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.step-status {
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: var(--font-mono);
}

.step-status.completed {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.step-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}

.toggle-icon {
  font-size: 0.7rem;
  color: var(--text-dim);
}

.step-details {
  padding: 0.85rem;
  border-top: 1px solid var(--border-light);
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.7rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.json-code {
  margin: 0;
  background: #000000;
  padding: 0.65rem;
  border-radius: 4px;
  color: #a7f3d0;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  overflow-x: auto;
  max-height: 250px;
}

.error-box {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--error);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
}
</style>
