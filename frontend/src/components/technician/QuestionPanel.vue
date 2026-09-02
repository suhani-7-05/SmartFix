<script setup>
defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  selectedModel: {
    type: String,
    required: true,
  },
  llmModels: {
    type: Array,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: "",
  },
  sampleQuestions: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue", "update:selectedModel", "ask"]);

function onInput(event) {
  emit("update:modelValue", event.target.value);
}

function useSample(text) {
  emit("update:modelValue", text);
}

function submitOnShortcut(event) {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
    emit("ask");
  }
}

function onModelChange(event) {
  emit("update:selectedModel", event.target.value);
}
</script>

<template>
  <section class="panel main-panel">
    <div class="panel-header">
      <h2 class="panel-title">Ask a question</h2>
      <span class="panel-hint">⌘/Ctrl + Enter to submit</span>
    </div>

    <div class="model-selector">
      <label for="llm-model-select" class="model-selector-label">LLM model</label>
      <select
        id="llm-model-select"
        class="model-select"
        :value="selectedModel"
        :disabled="isLoading"
        @change="onModelChange"
      >
        <option v-for="llm in llmModels" :key="llm.id" :value="llm.id">
          {{ llm.label }}
        </option>
      </select>
    </div>

    <label for="question-input" class="sr-only">Technical question</label>
    <textarea
      id="question-input"
      class="question-input"
      rows="5"
      :value="modelValue"
      :disabled="isLoading"
      placeholder="Example: How should I troubleshoot low hydraulic pressure?"
      @input="onInput"
      @keydown="submitOnShortcut"
    ></textarea>

    <div class="sample-questions">
      <span class="sample-label">Try:</span>
      <button
        v-for="sample in sampleQuestions"
        :key="sample"
        type="button"
        class="sample-chip"
        :disabled="isLoading"
        @click="useSample(sample)"
      >
        {{ sample }}
      </button>
    </div>

    <button type="button" class="ask-button" :disabled="isLoading" @click="emit('ask')">
      <span v-if="isLoading" class="btn-spinner" aria-hidden="true"></span>
      <span>{{ isLoading ? "Processing…" : "Ask SmartFix" }}</span>
    </button>

    <transition name="fade-slide">
      <div v-if="errorMessage" class="alert alert-error" role="alert">
        <svg class="alert-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
            clip-rule="evenodd"
          />
        </svg>
        <div>
          <strong>Something went wrong</strong>
          <p>{{ errorMessage }}</p>
        </div>
      </div>
    </transition>
  </section>
</template>
