<script setup>
defineProps({
  activeTab: {
    type: String,
    default: "technician",
  },
});

defineEmits(["select-tab"]);
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="28" height="28" rx="8" stroke="currentColor" stroke-width="2" />
            <path d="M10 16h12M16 10v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <circle cx="16" cy="16" r="4" fill="currentColor" />
          </svg>
        </div>
        <div class="brand-text">
          <h1 class="app-title">SmartFix</h1>
          <span class="app-subtitle">DevOps Equipment Troubleshooting Platform</span>
        </div>
      </div>

      <nav class="nav-tabs" aria-label="Dashboard Views">
        <button
          class="nav-tab"
          :class="{ active: activeTab === 'technician' }"
          @click="$emit('select-tab', 'technician')"
        >
          <span class="tab-icon">🛠️</span>
          <span class="tab-label">Technician Dashboard</span>
        </button>

        <button
          class="nav-tab"
          :class="{ active: activeTab === 'admin' }"
          @click="$emit('select-tab', 'admin')"
        >
          <span class="tab-icon">🔍</span>
          <span class="tab-label">Admin / AI Observability</span>
          <span class="tab-badge">Ex. 2</span>
        </button>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: var(--surface-bg, #111827);
  border-bottom: 1px solid var(--border-color, #1f2937);
  padding: 0.85rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  width: 36px;
  height: 36px;
  color: var(--primary-accent, #3b82f6);
}

.brand-icon svg {
  width: 100%;
  height: 100%;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.app-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.app-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted, #9ca3af);
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(17, 24, 39, 0.8);
  padding: 0.25rem;
  border-radius: 10px;
  border: 1px solid var(--border-color, #1f2937);
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-muted, #9ca3af);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-tab:hover {
  color: #f3f4f6;
  background: rgba(255, 255, 255, 0.05);
}

.nav-tab.active {
  background: var(--primary-accent, #3b82f6);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.tab-badge {
  font-size: 0.7rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  text-transform: uppercase;
}
</style>
