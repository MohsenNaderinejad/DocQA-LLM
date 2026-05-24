# API Documentation — Document Q&A System

Base URL: `http://localhost:8000/api`

---

## Documents

### List All Documents
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

### Upload a Document
```
POST /api/documents/
Content-Type: multipart/form-data
```

**Request body:**
| Field | Type | Required | Description |
|---|---|---|---|
| title | string | yes | Display name for the document |
| file | file | yes | The .docx file to upload |

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

> Note: `extracted_text` and `chunk_count` will be empty immediately after upload. Processing happens automatically in the background. Check the logs to see when it completes.

**Response `400 Bad Request`:**
```json
{
  "title": ["This field is required."],
  "file": ["No file was submitted."]
}
```

---

### Get a Single Document
```
GET /api/documents/<id>/
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

### Delete a Document
```
DELETE /api/documents/<id>/
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

### Ask a Question
```
POST /api/ask/
Content-Type: application/json
```

**Request body:**
| Field | Type | Required | Description |
|---|---|---|---|
| question | string | yes | The question to ask |

**Example:**
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

> Note: The answer is generated strictly from document content. If the answer cannot be found in the documents, the system will say so rather than making up an answer.

---

### Get Question History
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

## Error Reference

| Status Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request — missing or invalid fields |
| 404 | Resource not found |
| 500 | Server error — check logs |