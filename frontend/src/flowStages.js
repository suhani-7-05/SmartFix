/** Exercise 1 execution flow stages (no fake services). */
export const FLOW_STAGE_DEFS = [
  {
    id: "request-received",
    label: "Request Received",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0l4-4m-4 4L8 11"/><path d="M4 14v3a2 2 0 002 2h12a2 2 0 002-2v-3"/></svg>`,
  },
  {
    id: "smartfix-api",
    label: "SmartFix API",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><circle cx="7" cy="7" r="1" fill="currentColor"/><circle cx="7" cy="17" r="1" fill="currentColor"/></svg>`,
  },
  {
    id: "ollama-request",
    label: "Ollama Request",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a4 4 0 014 4v1h2a2 2 0 012 2v10a2 2 0 01-2 2H6a2 2 0 01-2-2V9a2 2 0 012-2h2V6a4 4 0 014-4z"/></svg>`,
  },
  {
    id: "code-llama",
    label: "LLM Generation",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 9l-3 3 3 3"/><path d="M16 9l3 3-3 3"/><path d="M13 6l-2 12"/></svg>`,
  },
  {
    id: "response-received",
    label: "Response Received",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path d="M9 12l2 2 4-4"/></svg>`,
  },
  {
    id: "response-displayed",
    label: "Response Displayed",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8"/></svg>`,
  },
];

export function createInitialFlowState() {
  return Object.fromEntries(FLOW_STAGE_DEFS.map((stage) => [stage.id, "pending"]));
}
