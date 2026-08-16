<script setup>
defineProps({
  activeTab: {
    type: String,
    default: "technician",
  },
  stats: {
    type: Object,
    default: () => ({
      documents: 0,
      chunks: 0,
      vector_store: { vector_count: 0 },
    }),
  },
});

defineEmits(["select-tab"]);
</script>

<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="4" />
          <path d="M12 8v8M8 12h8" />
        </svg>
      </div>
      <div class="brand-info">
        <span class="brand-name">SmartFix</span>
        <span class="brand-desc">DevOps Assistant</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="nav-menu">
      <div class="nav-section">
        <span class="section-label">Interfaces</span>

        <button
          class="nav-button"
          :class="{ active: activeTab === 'technician' }"
          @click="$emit('select-tab', 'technician')"
        >
          <svg class="nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
          </svg>
          <span>Troubleshooting</span>
        </button>

        <button
          class="nav-button"
          :class="{ active: activeTab === 'admin' }"
          @click="$emit('select-tab', 'admin')"
        >
          <svg class="nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          <span>Knowledge Base</span>
        </button>
      </div>
    </nav>

    <!-- Simple Status -->
    <div class="sidebar-status">
      <div class="status-row">
        <span class="status-dot"></span>
        <span class="status-name">Ollama</span>
        <span class="status-state">Ready</span>
      </div>
      <div class="status-row">
        <span class="status-name">Vectors</span>
        <span class="status-count">{{ stats.vector_store?.vector_count || 0 }}</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  padding: 1.25rem 0.85rem;
  box-sizing: border-box;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 0.5rem 1rem;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 1.25rem;
}

.brand-icon {
  width: 32px;
  height: 32px;
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon svg {
  width: 24px;
  height: 24px;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.brand-desc {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.nav-menu {
  flex: 1;
}

.nav-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.section-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
  padding: 0 0.5rem 0.35rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-button:hover {
  background: var(--border-light);
  color: var(--text-main);
}

.nav-button.active {
  background: var(--accent-light);
  color: var(--accent);
  border-color: rgba(59, 130, 246, 0.25);
  font-weight: 600;
}

.sidebar-status {
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.78rem;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-muted);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  margin-right: 0.4rem;
}

.status-name {
  color: var(--text-muted);
  flex: 1;
}

.status-state {
  color: var(--success);
  font-weight: 500;
}

.status-count {
  font-family: var(--font-mono);
  color: var(--text-main);
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    min-width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
}
</style>
