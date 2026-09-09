export const LLM_MODELS = [
  {
    id: "qwen2.5-coder:1.5b",
    label: "Qwen 2.5 Coder 1.5B (Ultra-Fast Edge)",
    params: "1.5B",
    specialization: "Fast Inference & Code Generation",
  },
  {
    id: "codellama",
    label: "Code Llama 7B (Deep Reasoning)",
    params: "7B",
    specialization: "Architecture, Explanation & Bug Analysis",
  },
  {
    id: "starcoder2:3b",
    label: "StarCoder2 3B (Syntax & Refactor)",
    params: "3B",
    specialization: "Code Completion & Refactoring",
  },
];

export const DEFAULT_LLM_MODEL = LLM_MODELS[0].id;

export const EVALUATION_CATEGORIES = [
  { id: "Explanation", label: "Explanation", desc: "Explaining internal functions and architectures" },
  { id: "Code Retrieval", label: "Code Retrieval", desc: "Locating files and implementation components" },
  { id: "Dependency Understanding", label: "Dependency Understanding", desc: "Tracing service calls and vector DB storage" },
  { id: "Bug Analysis", label: "Bug Analysis", desc: "Diagnosing exceptions, failures and root causes" },
  { id: "Code Generation", label: "Code Generation", desc: "Synthesizing regex parsers, routes, and unit tests" },
  { id: "Refactoring", label: "Refactoring", desc: "Async concurrency, batching, and semantic chunking" },
  { id: "RAG based Question", label: "RAG based Question", desc: "Grounded equipment troubleshooting via PDF manuals" },
];

export const CATEGORY_SAMPLE_QUESTIONS = [
  {
    category: "Explanation",
    question: "What does the search_similar() function in vector_store.py do?",
  },
  {
    category: "Code Retrieval",
    question: "Which file handles text chunking and character offset tracking for uploaded documents?",
  },
  {
    category: "Dependency Understanding",
    question: "Which microservices call the Equipment Service on port 8002?",
  },
  {
    category: "Bug Analysis",
    question: "What error occurs if an array truthiness check is evaluated on a NumPy vector returned by ChromaDB?",
  },
  {
    category: "Code Generation",
    question: "Write a Python function to parse equipment IDs like EQ-1023 from a query string.",
  },
  {
    category: "Refactoring",
    question: "Suggest an improvement to the HTTP service calls in orchestrator/main.py to improve latency.",
  },
  {
    category: "RAG based Question",
    question: "What is the mandatory safety precaution before replacing part HP-FLTR-05 on EQ-1023?",
  },
];
