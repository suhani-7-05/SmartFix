<script setup>
import { computed } from "vue";

const props = defineProps({
  flowStages: {
    type: Array,
    required: true,
  },
});

const flowSummary = computed(() => {
  const statuses = props.flowStages.map((stage) => stage.status);
  if (statuses.includes("error")) return "Error";
  if (statuses.every((status) => status === "completed")) return "Complete";
  if (statuses.some((status) => status === "processing")) return "Running";
  return "Idle";
});

function formatStatus(status) {
  const labels = {
    pending: "Pending",
    processing: "Processing",
    completed: "Completed",
    error: "Error",
  };
  return labels[status] || status;
}

function connectorClass(index) {
  const current = props.flowStages[index];
  const next = props.flowStages[index + 1];
  if (current.status === "error" || next.status === "error") return "error";
  if (current.status === "completed") return "completed";
  if (current.status === "processing") return "processing";
  return "pending";
}
</script>

<template>
  <aside class="panel flow-panel">
    <div class="panel-header">
      <h2 class="panel-title">Execution Flow</h2>
      <span class="flow-summary">{{ flowSummary }}</span>
    </div>

    <ol class="execution-flow">
      <li v-for="(stage, index) in flowStages" :key="stage.id" class="flow-item">
        <div class="flow-step" :class="stage.status">
          <div class="flow-icon-wrap">
            <span class="flow-icon" v-html="stage.icon"></span>
            <span
              v-if="stage.status === 'processing'"
              class="flow-pulse"
              aria-hidden="true"
            ></span>
          </div>
          <div class="flow-content">
            <span class="flow-name">{{ stage.label }}</span>
            <span class="flow-status">{{ formatStatus(stage.status) }}</span>
          </div>
        </div>
        <div
          v-if="index < flowStages.length - 1"
          class="flow-connector"
          :class="connectorClass(index)"
        ></div>
      </li>
    </ol>
  </aside>
</template>
