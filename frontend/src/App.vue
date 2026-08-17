<script setup>
import { computed, onMounted, ref } from "vue";
import SidebarNav from "./components/common/SidebarNav.vue";
import QuestionPanel from "./components/technician/QuestionPanel.vue";
import ResponsePanel from "./components/technician/ResponsePanel.vue";
import ExecutionFlow from "./components/technician/ExecutionFlow.vue";

import VectorStoreStats from "./components/admin/VectorStoreStats.vue";
import DocumentManager from "./components/admin/DocumentManager.vue";
import ChunkViewer from "./components/admin/ChunkViewer.vue";
import EmbeddingViewer from "./components/admin/EmbeddingViewer.vue";
import ExecutionTraceViewer from "./components/admin/ExecutionTraceViewer.vue";
import RAGRetrievedContextViewer from "./components/admin/RAGRetrievedContextViewer.vue";
import SafetyAndEquipmentViewer from "./components/admin/SafetyAndEquipmentViewer.vue";

import { callAskApi } from "./api/askApi.js";
import {
  deleteDocument,
  fetchDocumentChunks,
  fetchDocuments,
  fetchKbStats,
  fetchVectorInfo,
  uploadDocument,
} from "./api/kbApi.js";
import { FLOW_STAGE_DEFS, createInitialFlowState } from "./flowStages.js";

// Active Dashboard Tab ('technician' | 'admin')
const activeTab = ref("technician");

// --- Technician & Orchestrated State ---
const question = ref("EQ-1023 has low hydraulic pressure. How do I fix it?");
const answer = ref("");
const model = ref("");
const errorMessage = ref("");
const isLoading = ref(false);
const flowState = ref(createInitialFlowState());

// Orchestration & Observability Data
const orchestrationData = ref({
  execution_trace: [],
  total_duration_ms: 0,
  rag: {},
  safety: {},
  equipment: {},
  history: {},
  spare_parts: {},
  ticket: {},
});

const sampleQuestions = [
  "EQ-1023 has low hydraulic pressure. How do I fix it?",
  "How do I clear a jammed belt on conveyor EQ-2045?",
  "EQ-3081 stator temperature high. Can I open terminal box while live?",
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
    errorMessage.value = "Please enter a question before submitting.";
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

    answer.value = data.answer || "No response received.";
    model.value = data.model || "codellama";

    if (data.execution_trace) {
      orchestrationData.value = data;
    }

    completeFlow();
  } catch (error) {
    failFlow();
    errorMessage.value =
      error.message || "Something went wrong while contacting SmartFix backend.";
  } finally {
    isLoading.value = false;
  }
}

// --- Knowledge Base State (Exercise 2) ---
const kbStats = ref({
  documents: 0,
  chunks: 0,
  embedded_chunks: 0,
  vector_store: { collection: "smartfix_chunks", vector_count: 0 },
});
const kbStatsLoading = ref(false);
const documents = ref([]);
const selectedDocId = ref(null);
const selectedDoc = computed(() =>
  documents.value.find((d) => d.id === selectedDocId.value) || null
);

const chunks = ref([]);
const chunksLoading = ref(false);

const selectedChunk = ref(null);
const vectorData = ref(null);
const vectorLoading = ref(false);

const isUploading = ref(false);
const uploadError = ref("");

async function loadKbStats() {
  kbStatsLoading.value = true;
  try {
    kbStats.value = await fetchKbStats();
  } catch (e) {
    console.error("Failed to load KB stats:", e);
  } finally {
    kbStatsLoading.value = false;
  }
}

async function loadDocuments() {
  try {
    documents.value = await fetchDocuments();
    if (documents.value.length > 0 && !selectedDocId.value) {
      handleSelectDoc(documents.value[0].id);
    }
  } catch (e) {
    console.error("Failed to load documents:", e);
  }
}

async function handleUpload(file) {
  isUploading.value = true;
  uploadError.value = "";
  try {
    const doc = await uploadDocument(file);
    await loadDocuments();
    await loadKbStats();
    if (doc && doc.id) {
      handleSelectDoc(doc.id);
    }
  } catch (err) {
    uploadError.value = err.message || "Upload failed.";
  } finally {
    isUploading.value = false;
  }
}

async function handleSelectDoc(docId) {
  selectedDocId.value = docId;
  chunks.value = [];
  selectedChunk.value = null;
  vectorData.value = null;

  if (!docId) return;

  chunksLoading.value = true;
  try {
    chunks.value = await fetchDocumentChunks(docId);
    if (chunks.value.length > 0) {
      handleSelectChunk(chunks.value[0]);
    }
  } catch (e) {
    console.error("Failed to load chunks:", e);
  } finally {
    chunksLoading.value = false;
  }
}

async function handleSelectChunk(chunk) {
  selectedChunk.value = chunk;
  vectorData.value = null;

  if (!chunk || !chunk.vector_id) return;

  vectorLoading.value = true;
  try {
    vectorData.value = await fetchVectorInfo(chunk.vector_id);
  } catch (e) {
    console.error("Failed to load vector details:", e);
  } finally {
    vectorLoading.value = false;
  }
}

async function handleDeleteDoc(docId) {
  if (!confirm("Are you sure you want to delete this document and all associated vectors?")) return;
  try {
    await deleteDocument(docId);
    if (selectedDocId.value === docId) {
      selectedDocId.value = null;
      chunks.value = [];
      selectedChunk.value = null;
      vectorData.value = null;
    }
    await loadDocuments();
    await loadKbStats();
  } catch (e) {
    alert("Delete failed: " + e.message);
  }
}

onMounted(() => {
  loadKbStats();
  loadDocuments();
});
</script>

<template>
  <div class="app-layout">
    <!-- Left Sidebar Navbar -->
    <SidebarNav
      :active-tab="activeTab"
      :stats="kbStats"
      @select-tab="activeTab = $event"
    />

    <!-- Main View Panel -->
    <div class="main-content">
      <!-- Technician View (Exercise 1 & Final Flow) -->
      <div v-if="activeTab === 'technician'" class="view-container">
        <div class="page-header">
          <h2>Equipment Troubleshooting</h2>
          <p>Ask technical questions about equipment and receive diagnostic guidance powered by Code Llama.</p>
        </div>

        <div class="layout">
          <div class="main-column">
            <QuestionPanel
              v-model="question"
              :is-loading="isLoading"
              :error-message="errorMessage"
              :sample-questions="sampleQuestions"
              @ask="askSmartFix"
            />
            <ResponsePanel
              :answer="answer"
              :model="model"
              :safety-decision="orchestrationData.safety?.decision"
              :ticket="orchestrationData.ticket"
              :spare-parts="orchestrationData.spare_parts"
              :equipment="orchestrationData.equipment"
            />

          </div>

          <ExecutionFlow :flow-stages="flowStages" />
        </div>
      </div>

      <!-- Admin Observability View (Exercises 2, 3, 4, 5) -->
      <div v-else-if="activeTab === 'admin'" class="view-container">
        <div class="page-header">
          <h2>AI & Microservices Observability Dashboard</h2>
          <p>Inspect real orchestrator execution traces, RAG vector similarity, Safety Engine decisions, equipment specs, and vector DB storage.</p>
        </div>

        <!-- Real Execution Trace (Exercise 4 Orchestration) -->
        <ExecutionTraceViewer
          :trace="orchestrationData.execution_trace"
          :total-duration-ms="orchestrationData.total_duration_ms"
        />

        <!-- RAG Search & Vector Retrieval (Exercise 3 RAG) -->
        <RAGRetrievedContextViewer
          :rag-data="orchestrationData.rag"
        />

        <!-- Safety Engine, Equipment, History & Parts (Exercise 4 Microservices) -->
        <SafetyAndEquipmentViewer
          :safety="orchestrationData.safety"
          :equipment="orchestrationData.equipment"
          :history="orchestrationData.history"
          :spare-parts="orchestrationData.spare_parts"
          :ticket="orchestrationData.ticket"
        />

        <!-- Knowledge Base & Vector Ingestion (Exercise 2) -->
        <VectorStoreStats :stats="kbStats" :loading="kbStatsLoading" />

        <DocumentManager
          :documents="documents"
          :selected-doc-id="selectedDocId"
          :uploading="isUploading"
          :upload-error="uploadError"
          @upload="handleUpload"
          @select-doc="handleSelectDoc"
          @delete-doc="handleDeleteDoc"
        />

        <div class="grid-2col">
          <ChunkViewer
            :document="selectedDoc"
            :chunks="chunks"
            :selected-chunk-id="selectedChunk?.id"
            :loading="chunksLoading"
            @select-chunk="handleSelectChunk"
          />

          <EmbeddingViewer
            :chunk="selectedChunk"
            :vector-data="vectorData"
            :loading="vectorLoading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-main);
}

.main-content {
  flex: 1;
  padding: 2rem 2.5rem;
  max-width: 1400px;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.page-header p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .grid-2col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .main-content {
    padding: 1.25rem 1rem;
  }
}
</style>
