<script setup>
defineProps({
  equipment: {
    type: Object,
    default: () => ({}),
  },
  safety: {
    type: Object,
    default: () => ({}),
  },
  history: {
    type: Object,
    default: () => ({}),
  },
  spareParts: {
    type: Object,
    default: () => ({}),
  },
  ticket: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<template>
  <div class="grid-2col">
    <!-- Safety Engine Inspection Card -->
    <div class="card">
      <div class="card-header">
        <h3>Safety Engine Decision</h3>
        <span class="decision-badge" :class="safety.decision?.toLowerCase() || 'allowed'">
          {{ safety.decision || 'ALLOWED' }}
        </span>
      </div>

      <div v-if="!safety.decision" class="state-box">
        No safety evaluation data available yet.
      </div>

      <div v-else class="safety-content">
        <div v-if="safety.warnings && safety.warnings.length > 0" class="warning-box">
          <span class="box-title">Active Safety Warnings:</span>
          <ul>
            <li v-for="(w, i) in safety.warnings" :key="i">{{ w }}</li>
          </ul>
        </div>

        <div class="precaution-box">
          <span class="box-title">Mandatory Safety Precautions:</span>
          <ul>
            <li v-for="(p, i) in safety.required_precautions" :key="i">{{ p }}</li>
          </ul>
        </div>

        <div v-if="safety.rules_triggered && safety.rules_triggered.length > 0" class="rules-box">
          <span class="box-title">Rules Triggered:</span>
          <div class="tag-list">
            <span v-for="(r, i) in safety.rules_triggered" :key="i" class="rule-tag">{{ r }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Equipment & History Inspection Card -->
    <div class="card">
      <div class="card-header">
        <h3>Equipment & Maintenance History</h3>
        <span class="card-sub">{{ equipment.equipment_id || 'EQ-1023' }}</span>
      </div>

      <div v-if="!equipment.name" class="state-box">
        No equipment data fetched yet.
      </div>

      <div v-else class="eq-content">
        <div class="eq-info">
          <div class="info-row">
            <span class="label">Equipment Name:</span>
            <span class="val font-medium">{{ equipment.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Model & Category:</span>
            <span class="val">{{ equipment.model }} ({{ equipment.category }})</span>
          </div>
          <div class="info-row">
            <span class="label">Location:</span>
            <span class="val">{{ equipment.location }}</span>
          </div>
        </div>

        <div class="history-list">
          <span class="box-title">Past Maintenance Events ({{ history.event_count || 0 }}):</span>
          <div v-if="!history.history || history.history.length === 0" class="no-history">
            No previous repair records.
          </div>
          <div v-for="evt in history.history" :key="evt.event_id" class="history-item">
            <div class="evt-header">
              <span class="evt-date font-mono">{{ evt.date }}</span>
              <span class="evt-type">{{ evt.type }}</span>
            </div>
            <div class="evt-body">
              <strong>Symptom:</strong> {{ evt.symptom }}<br />
              <strong>Action:</strong> {{ evt.action_taken }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Spare Parts & Ticket Card -->
    <div class="card col-span-2">
      <div class="card-header">
        <h3>Spare Parts & Service Tickets</h3>
        <span v-if="ticket && ticket.ticket_id" class="ticket-badge">
          Created {{ ticket.ticket_id }} ({{ ticket.status }})
        </span>
      </div>

      <div class="parts-grid">
        <div class="parts-col">
          <span class="box-title">Compatible Spare Parts Inventory:</span>
          <div v-if="!spareParts.parts || spareParts.parts.length === 0" class="no-history">
            No spare parts data.
          </div>
          <table v-else class="mini-table">
            <thead>
              <tr>
                <th>Part #</th>
                <th>Name</th>
                <th>Stock Status</th>
                <th>Qty</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pt in spareParts.parts" :key="pt.part_number">
                <td class="font-mono">{{ pt.part_number }}</td>
                <td class="font-medium">{{ pt.name }}</td>
                <td>
                  <span class="stock-badge" :class="pt.stock_status.toLowerCase()">
                    {{ pt.stock_status }}
                  </span>
                </td>
                <td>{{ pt.quantity_available }}</td>
                <td>{{ pt.location_bin }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="ticket && ticket.ticket_id" class="ticket-box">
          <span class="box-title">Automated Field Ticket Dispatch</span>
          <div class="ticket-details">
            <div><strong>Ticket ID:</strong> <span class="font-mono text-accent">{{ ticket.ticket_id }}</span></div>
            <div><strong>Priority:</strong> {{ ticket.priority }}</div>
            <div><strong>Assigned:</strong> {{ ticket.assigned_team }}</div>
            <div><strong>Summary:</strong> {{ ticket.issue_summary }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.col-span-2 {
  grid-column: 1 / -1;
}

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
  font-size: 1rem;
  font-weight: 600;
}

.card-sub {
  font-size: 0.78rem;
  color: var(--text-dim);
}

.state-box {
  padding: 1.5rem;
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-dim);
  background: rgba(0, 0, 0, 0.15);
  border-radius: var(--radius);
}

.decision-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.78rem;
}

.decision-badge.allowed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.decision-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.decision-badge.blocked {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error);
}

.safety-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.box-title {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.35rem;
}

.warning-box {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: var(--warning);
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
}

.warning-box ul,
.precaution-box ul {
  margin: 0;
  padding-left: 1.2rem;
}

.precaution-box {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-light);
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  color: var(--text-main);
}

.rule-tag {
  font-size: 0.72rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: var(--text-muted);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.eq-info {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.82rem;
  margin-bottom: 0.85rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
}

.label {
  color: var(--text-dim);
}

.val {
  color: var(--text-main);
}

.font-medium {
  font-weight: 500;
}

.font-mono {
  font-family: var(--font-mono);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-light);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.78rem;
}

.evt-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.evt-date {
  color: var(--accent);
}

.evt-type {
  color: var(--text-dim);
}

.evt-body {
  color: var(--text-muted);
  line-height: 1.4;
}

.parts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
}

.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
  text-align: left;
}

.mini-table th {
  padding: 0.4rem 0.5rem;
  background: rgba(0, 0, 0, 0.25);
  color: var(--text-dim);
  border-bottom: 1px solid var(--border-color);
}

.mini-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-muted);
}

.stock-badge {
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  font-size: 0.68rem;
  font-weight: 600;
}

.stock-badge.in_stock {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.stock-badge.low_stock {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.stock-badge.out_of_stock {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error);
}

.ticket-box {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  padding: 0.75rem;
  border-radius: var(--radius);
}

.ticket-details {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--text-main);
}

.ticket-badge {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: var(--font-mono);
}

.text-accent {
  color: var(--accent);
}

@media (max-width: 900px) {
  .grid-2col,
  .parts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
