/**
 * SmartFix Multi-Model & Technician API Client
 */

export async function callAskApi(questionText, model) {
  const response = await fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: questionText, model }),
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export async function callCompareApi(questionText) {
  const response = await fetch("/compare", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: questionText }),
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export async function fetchBenchmarkResults() {
  const response = await fetch("/benchmark/results");
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} fetching benchmark data`);
  }
  return response.json();
}
