<script setup>
import { computed, ref } from "vue";
import { callAskApi } from "./api.js";
import ExecutionFlow from "./components/ExecutionFlow.vue";
import QuestionPanel from "./components/QuestionPanel.vue";
import ResponsePanel from "./components/ResponsePanel.vue";
import { FLOW_STAGE_DEFS, createInitialFlowState } from "./flowStages.js";

const question = ref("");
const answer = ref("");
const model = ref("");
const errorMessage = ref("");
const isLoading = ref(false);
const flowState = ref(createInitialFlowState());

const sampleQuestions = [
  "How should I troubleshoot low hydraulic pressure?",
  "What causes overheating in industrial pumps?",
  "How do I safely inspect a conveyor belt motor?",
];

const flowStages = computed(() =>
  FLOW_STAGE_DEFS.map((stage) => ({
    ...stage,
    status: flowState.value[stage.id],
  }))
);

function setStageStatus(stageId, status) {
  if (flowState.value[stageId] !== undefined) {
    flowState.value = { ...flowState.value, [stageId]: status };
  }
}

function resetFlow() {
  flowState.value = createInitialFlowState();
}

function advanceFlowTo(stageId) {
  const next = { ...flowState.value };
  let reached = false;

  FLOW_STAGE_DEFS.forEach((stage) => {
    if (stage.id === stageId) {
      next[stage.id] = "processing";
      reached = true;
      return;
    }
    if (!reached) {
      next[stage.id] = "completed";
    }
  });

  flowState.value = next;
}

function completeFlow() {
  flowState.value = Object.fromEntries(
    FLOW_STAGE_DEFS.map((stage) => [stage.id, "completed"])
  );
}

function failFlow() {
  const next = { ...flowState.value };
  let errorAssigned = false;

  FLOW_STAGE_DEFS.forEach((stage) => {
    if (!errorAssigned && next[stage.id] === "processing") {
      next[stage.id] = "error";
      errorAssigned = true;
      return;
    }
    if (!errorAssigned && next[stage.id] === "pending") {
      next[stage.id] = "error";
    }
  });

  flowState.value = next;
}

function clearOutput() {
  answer.value = "";
  model.value = "";
  errorMessage.value = "";
}

async function askSmartFix() {
  const text = question.value.trim();

  clearOutput();
  resetFlow();
  isLoading.value = true;

  setStageStatus("request-received", "completed");
  advanceFlowTo("smartfix-api");

  if (!text) {
    isLoading.value = false;
    failFlow();
    errorMessage.value = "Please enter a question before asking SmartFix.";
    return;
  }

  try {
    advanceFlowTo("ollama-request");
    const apiPromise = callAskApi(text);
    advanceFlowTo("code-llama");

    const data = await apiPromise;

    setStageStatus("code-llama", "completed");
    advanceFlowTo("response-received");
    setStageStatus("response-received", "completed");
    advanceFlowTo("response-displayed");

    answer.value = data.answer;
    model.value = data.model;
    completeFlow();
  } catch (error) {
    failFlow();
    errorMessage.value =
      error.message || "Something went wrong while contacting SmartFix.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="page-bg"></div>

  <main class="app-shell">
    <header class="hero">
      <div class="hero-badge">Exercise 1 · LLM Assistant</div>
      <div class="hero-brand">
        <div class="logo-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="28" height="28" rx="8" stroke="currentColor" stroke-width="2" />
            <path d="M10 16h12M16 10v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <circle cx="16" cy="16" r="4" fill="currentColor" />
          </svg>
        </div>
        <div>
          <h1 class="logo">SmartFix</h1>
          <p class="tagline">AI-powered equipment troubleshooting assistant</p>
        </div>
      </div>
      <p class="hero-desc">
        Ask technical maintenance questions and get guidance from Code Llama via your local Ollama
        runtime.
      </p>
    </header>

    <div class="layout">
      <div class="main-column">
        <QuestionPanel
          v-model="question"
          :is-loading="isLoading"
          :error-message="errorMessage"
          :sample-questions="sampleQuestions"
          @ask="askSmartFix"
        />
        <ResponsePanel :answer="answer" :model="model" />
      </div>

      <ExecutionFlow :flow-stages="flowStages" />
    </div>

    <footer class="footer">
      <span>User → Frontend → FastAPI → Ollama → Code Llama → Response</span>
    </footer>
  </main>
</template>
