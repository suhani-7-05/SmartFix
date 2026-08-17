<script setup>
defineProps({
  answer: {
    type: String,
    default: "",
  },
  model: {
    type: String,
    default: "",
  },
  safetyDecision: {
    type: String,
    default: "ALLOWED",
  },
  ticket: {
    type: Object,
    default: () => ({}),
  },
  spareParts: {
    type: Object,
    default: () => ({}),
  },
  equipment: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<template>
  <transition name="fade-slide">
    <section v-if="answer" class="panel response-panel">
      <!-- Response Header & Badges -->
      <div class="response-header">
        <div class="title-wrap">
          <h2 class="panel-title">Diagnostic Response</h2>
          <span
            v-if="safetyDecision"
            class="safety-badge"
            :class="safetyDecision.toLowerCase()"
          >
            Safety: {{ safetyDecision }}
          </span>
        </div>
        <span v-if="model" class="model-badge">{{ model }}</span>
      </div>

      <!-- Ticket Created Alert Banner (If ticket was generated) -->
      <div v-if="ticket && ticket.ticket_id" class="ticket-banner">
        <div class="ticket-icon">🎫</div>
        <div class="ticket-info">
          <strong>Service Ticket Dispatched: {{ ticket.ticket_id }}</strong>
          <span>Priority: {{ ticket.priority }} | Status: {{ ticket.status }} | Assigned: {{ ticket.assigned_team }}</span>
        </div>
      </div>

      <!-- Main Answer Body -->
      <p class="response-text">{{ answer }}</p>

      <!-- Quick Spare Parts Availability Bar -->
      <div v-if="spareParts && spareParts.parts && spareParts.parts.length > 0" class="parts-bar">
        <span class="parts-label">Compatible Spare Parts:</span>
        <div class="parts-tags">
          <span v-for="pt in spareParts.parts" :key="pt.part_number" class="part-chip">
            <code>{{ pt.part_number }}</code> ({{ pt.stock_status.replace('_', ' ') }})
          </span>
        </div>
      </div>
    </section>
  </transition>
</template>

<style scoped>
.title-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.safety-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.safety-badge.allowed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.safety-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.safety-badge.blocked {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error);
}

.ticket-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.ticket-icon {
  font-size: 1.25rem;
}

.ticket-info {
  display: flex;
  flex-direction: column;
}

.ticket-info strong {
  color: var(--error);
}

.ticket-info span {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.parts-bar {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}

.parts-label {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.parts-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.part-chip {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: var(--text-muted);
}

.part-chip code {
  color: var(--accent);
  font-family: var(--font-mono);
}
</style>
