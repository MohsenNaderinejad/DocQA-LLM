# API Documentation — DocQA-LLM (Document Q&A System)

This document describes the REST API for **DocQA-LLM**, a Django-based Document Question Answering system.

## Base URLs

The API is served under `/api/`.

- **Docker / Compose (recommended):** `http://localhost:8000/api`
- **Local run (without Docker):** `http://127.0.0.1:8000/api`

> Tip: Both URLs point to the same server *on your machine*. Use whichever matches how you run Django.

---

## Typical Testing Workflow (Recommended)

1. **Upload one or more `.docx` documents** via `/api/documents/` or Django Admin.
2. **Wait for background processing** (text extraction → chunking → embedding generation).
   - Right after upload, `extracted_text` may be empty and `chunk_count` may be `0`.
   - In Docker, you can monitor processing logs with:
     ```bash
     docker compose logs -f web
     ```
3. **Ask a question** via `/api/ask/`.
4. **Verify history is stored** via `/api/history/` or Django Admin.

---

## Documents

### 1) List All Documents

```
GET /api/documents/
```

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Employment Contract",
    "file": "http://localhost:8000/media/documents/contract.docx",
    "extracted_text": "This employment contract is made between...",
    "uploaded_at": "2026-05-18T21:05:00Z",
    "updated_at": "2026-05-18T21:05:00Z",
    "chunk_count": 6
  }
]
```

---

### 2) Upload a Document

```
POST /api/documents/
Content-Type: multipart/form-data
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| title | string | yes | Display name for the document |
| file | file | yes | The `.docx` file to upload |

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -F "title=Employment Contract" \
  -F "file=@/path/to/contract.docx"
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "title": "Employment Contract",
  "file": "http://localhost:8000/media/documents/contract.docx",
  "extracted_text": "",
  "uploaded_at": "2026-05-18T21:05:00Z",
  "updated_at": "2026-05-18T21:05:00Z",
  "chunk_count": 0
}
```

**Important notes (processing delay):**
- `extracted_text` and `chunk_count` can be empty immediately after upload.
- Document processing is triggered automatically after creation:
  - `.docx` text extraction
  - chunking
  - embedding generation

**Response `400 Bad Request`:**
```json
{
  "title": ["This field is required."],
  "file": ["No file was submitted."]
}
```

---

### 3) Get a Single Document

```
GET /api/documents/{id}/
```

**Example:**
```bash
curl http://localhost:8000/api/documents/1/
```

**Response `200 OK`:**
```json
{
  "id": 1,
  "title": "Employment Contract",
  "file": "http://localhost:8000/media/documents/contract.docx",
  "extracted_text": "This employment contract is made between Acme Corp and John Smith...",
  "uploaded_at": "2026-05-18T21:05:00Z",
  "updated_at": "2026-05-18T21:05:00Z",
  "chunk_count": 6
}
```

**Response `404 Not Found`:**
```json
{
  "error": "Document not found"
}
```

---

### 4) Delete a Document

```
DELETE /api/documents/{id}/
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/documents/1/
```

**Response `200 OK`:**
```json
{
  "message": "Document 'Employment Contract' deleted successfully"
}
```

> Note: Deleting a document also deletes the physical file from disk and all associated chunks and embeddings.

**Response `404 Not Found`:**
```json
{
  "error": "Document not found"
}
```

---

## Question & Answer

### 1) Ask a Question

```
POST /api/ask/
Content-Type: application/json
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| question | string | yes | The question to ask |

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the contract duration?"}'
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "question": "What is the contract duration?",
  "answer": "Based on the provided documents, the contract duration is 2 years from the signing date of January 15th, 2024.",
  "sources": ["Employment Contract"],
  "created_at": "2026-05-18T21:10:00Z"
}
```

**Response `400 Bad Request`:**
```json
{
  "error": "Question cannot be empty"
}
```

**Response `500 Internal Server Error`:**
```json
{
  "error": "error details here"
}
```

**Important notes (retrieval + accuracy):**
- The answer is generated strictly from the retrieved document context.
- If the answer is not present in the uploaded documents, the system should say so (instead of hallucinating).
- If you ask a question immediately after upload, the system may not retrieve anything yet because embeddings are still being generated.

---

### 2) Get Question History

```
GET /api/history/
```

**Example:**
```bash
curl http://localhost:8000/api/history/
```

**Response `200 OK`:**
```json
[
  {
    "id": 2,
    "question": "Who signed the contract?",
    "answer": "The contract was signed by John Smith on behalf of the employee.",
    "sources": ["Employment Contract"],
    "created_at": "2026-05-18T21:15:00Z"
  },
  {
    "id": 1,
    "question": "What is the contract duration?",
    "answer": "The contract duration is 2 years from the signing date.",
    "sources": ["Employment Contract"],
    "created_at": "2026-05-18T21:10:00Z"
  }
]
```

> Returns the last 20 entries, ordered by most recent first.

---

## Field Reference

### Document object

| Field | Meaning |
|---|---|
| id | Document ID |
| title | Human-readable title |
| file | URL to the uploaded file (served from `/media/`) |
| extracted_text | Full extracted text from `.docx` |
| uploaded_at | Upload timestamp |
| updated_at | Update timestamp |
| chunk_count | Number of chunks generated for retrieval |

### QAHistory object

| Field | Meaning |
|---|---|
| id | Q&A history record ID |
| question | User question |
| answer | Generated answer |
| sources | Document titles used as sources (based on retrieved chunks) |
| created_at | Timestamp |

---

## Error Reference

| Status Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request — missing or invalid fields |
| 404 | Resource not found |
| 500 | Server error — check logs |

---

## Common Issues / Debug Tips

### 1) OpenRouter / API key errors
- Ensure `.env` contains `OPENROUTER_API_KEY`.
- Restart Docker containers after changing `.env`:
  ```bash
  docker compose down
  docker compose up --build
  ```

### 2) Asking questions but getting “no relevant documents”
- Make sure you uploaded documents and waited for embedding generation to finish.
- In Docker, check logs:
  ```bash
  docker compose logs -f web
  ```

### 3) Upload errors
- Ensure you use `multipart/form-data` and pass both fields: `title` and `file`.
- Ensure the uploaded file is a real `.docx`.