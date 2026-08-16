/**
 * SmartFix Exercise 2 API Client — Knowledge Base & Vector Observability
 */

export async function fetchKbStats() {
  const res = await fetch("/kb/stats");
  if (!res.ok) throw new Error(`Failed to fetch KB stats: ${res.statusText}`);
  return res.json();
}

export async function fetchDocuments() {
  const res = await fetch("/kb/documents");
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/kb/documents/upload", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorDetail = `Upload failed (${res.status})`;
    try {
      const err = await res.json();
      if (err.detail) errorDetail = err.detail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export async function fetchDocumentChunks(documentId) {
  const res = await fetch(`/kb/documents/${documentId}/chunks`);
  if (!res.ok) throw new Error(`Failed to fetch document chunks: ${res.statusText}`);
  return res.json();
}

export async function fetchVectorInfo(vectorId) {
  const res = await fetch(`/kb/vectors/${vectorId}`);
  if (!res.ok) throw new Error(`Failed to fetch vector details: ${res.statusText}`);
  return res.json();
}

export async function deleteDocument(documentId) {
  const res = await fetch(`/kb/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Failed to delete document: ${res.statusText}`);
  return res.json();
}
