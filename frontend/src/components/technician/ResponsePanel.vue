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
});
</script>

<template>
  <transition name="fade-slide">
    <section v-if="answer" class="panel response-panel">
      <div class="response-header">
        <h2 class="panel-title">Response</h2>
        <span v-if="model" class="model-badge">{{ model }}</span>
      </div>
      <p class="response-text">{{ answer }}</p>
    </section>
  </transition>
</template>
