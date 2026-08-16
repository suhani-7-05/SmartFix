/**
 * SmartFix Exercise 1 API Client — Technician / Ask API
 */

export async function callAskApi(questionText) {
  const response = await fetch("/ask", {
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
      // Use fallback error message
    }
    throw new Error(errorMessage);
  }

  return response.json();
}
