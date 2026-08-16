/**
 * Call the SmartFix backend POST /ask endpoint.
 * Vite dev server proxies /ask to FastAPI on port 8000.
 */
export async function callAskApi(question) {
  const response = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg).join(" ")
          : "The request failed. Please try again.";
    throw new Error(message);
  }

  return data;
}
