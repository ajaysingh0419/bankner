<div align="center">

# 🏦 BankNER

### Production-Grade Named Entity Recognition for Banking & Insurance

*Extract. Classify. Audit. In milliseconds.*

![BankNER UI](screenshot.png)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-09A3D5?style=flat-square&logo=spacy&logoColor=white)](https://spacy.io)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-FF6B6B?style=flat-square)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## The Problem

Banks and insurance companies process thousands of documents daily — wire transfer instructions, KYC forms, loan agreements, claim submissions, trade confirmations. Every one of these contains sensitive entities: account numbers, IBANs, SSNs, policy IDs, SWIFT codes.

**Manually finding and extracting these entities is slow, error-prone, and doesn't scale.**

Existing ML-based NER solutions require:
- Cloud API calls (data residency violations)
- Expensive GPU inference (200–500ms per document)
- Black-box models that compliance teams can't audit or sign off on

BankNER solves all three. It runs **on your infrastructure**, processes documents in **under 15ms**, and every detection rule is **human-readable and auditable**.

---

## What BankNER Does

BankNER is a full-stack document intelligence platform that:

1. **Accepts** raw text documents via a browser UI, REST API, or WebSocket connection
2. **Scans** the document using a library of financial entity patterns
3. **Classifies** every match by entity type, confidence score, and sensitivity level
4. **Streams** results back to the UI in real-time as entities are found
5. **Scores** the document with a composite risk score based on what was found
6. **Exports** all findings as structured JSON or CSV for downstream processing

Everything runs locally. No document ever leaves your network.

---

## Live Demo — What It Detects

Feed BankNER this text:

```
Wire to IBAN GB29NWBK60161331926819, SWIFT NWBKGB2L.
Amount: $2,500,000.00. Sender SSN: 456-78-9012.
Policy POLHLT-2023-447821. Contact: Dr. Sarah Mitchell at sarah@bank.com
```

And it returns in **0.3ms**:

| Entity Text | Label | Confidence | Sensitivity |
|---|---|---|---|
| `GB29NWBK60161331926819` | IBAN | 97% | 🔴 HIGH |
| `NWBKGB2L` | SWIFT_BIC | 85% | 🟡 MEDIUM |
| `$2,500,000.00` | CURRENCY_AMOUNT | 92% | 🟢 LOW |
| `456-78-9012` | SSN | 97% | 🚨 CRITICAL |
| `POLHLT-2023-447821` | POLICY_ID | 82% | 🟡 MEDIUM |
| `Dr. Sarah Mitchell` | PERSON | 87% | 🟡 MEDIUM |
| `sarah@bank.com` | EMAIL | 99% | 🟡 MEDIUM |

---

## Full Entity Type Library

| Entity Type | Pattern Example | Use Case | Sensitivity |
|---|---|---|---|
| `ACCOUNT_NUMBER` | `4521890123456789` | Wire transfers, payments | 🔴 HIGH |
| `IBAN` | `GB29NWBK60161331926819` | International transfers | 🔴 HIGH |
| `SWIFT_BIC` | `NWBKGB2L` | Correspondent banking | 🟡 MEDIUM |
| `ROUTING_NUMBER` | `021000021` | US domestic transfers | 🔴 HIGH |
| `SSN` | `456-78-9012` | US identity verification | 🚨 CRITICAL |
| `CREDIT_CARD` | `4532015112830366` | PCI-DSS compliance | 🚨 CRITICAL |
| `PAN` | `BKQPS8832P` | India tax / KYC | 🔴 HIGH |
| `TAX_ID / EIN` | `47-1234567` | Corporate identity | 🔴 HIGH |
| `POLICY_ID` | `POLHLT-2023-447821` | Insurance processing | 🟡 MEDIUM |
| `CLAIM_NUMBER` | `CLM-2024-089234` | Claims management | 🟢 LOW |
| `LOAN_ID` | `LN-2024-087654` | Loan servicing | 🟡 MEDIUM |
| `CURRENCY_AMOUNT` | `$2,500,000.00` | Transaction amounts | 🟢 LOW |
| `PERSON` | `Dr. Sarah Mitchell` | KYC, AML screening | 🟡 MEDIUM |
| `ORG` | `NatWest Bank plc` | Counterparty identification | 🟢 LOW |
| `EMAIL` | `compliance@bank.com` | Contact extraction | 🟡 MEDIUM |
| `PHONE` | `+1-212-555-0187` | Contact extraction | 🟡 MEDIUM |
| `DATE` | `15 March 2024` | Timeline extraction | 🟢 LOW |

---

## Tech Stack

### Backend

| Technology | Version | Role |
|---|---|---|
| **Python** | 3.10+ | Core language |
| **FastAPI** | 0.111+ | REST API framework — async, OpenAPI spec auto-generated |
| **Uvicorn** | 0.29+ | ASGI server — handles HTTP and WebSocket on the same port |
| **spaCy** | 3.7+ | NLP pipeline infrastructure — `EntityRuler`, tokenizer, blank model |
| **WebSockets** | 12.0+ | Real-time bidirectional communication for streaming entity results |
| **Pydantic v2** | 2.7+ | Request/response validation and serialization |
| **Python `re`** | stdlib | Compiled regex engine — core pattern matching |
| **asyncio** | stdlib | Async event loop — non-blocking I/O for WebSocket streaming |

### Frontend

| Technology | Role |
|---|---|
| **Vanilla JS (ES2020)** | No framework, no build step — single `index.html` file |
| **WebSocket API** | Native browser WebSocket for real-time entity streaming |
| **CSS Variables + Grid** | Theming system, responsive 3-column layout |
| **Google Fonts (Syne + DM Mono)** | Typography — display + monospace pairing |

### Why no React/Vue?

The UI is a single `index.html` with zero dependencies. This is intentional — banks operate in environments where npm registries may be blocked, builds can't run, and IT security reviews every installed package. A self-contained HTML file passes security review in minutes.

### Why spaCy over Hugging Face transformers?

| | spaCy (BankNER) | Transformer NER |
|---|---|---|
| Inference time | ~0.3–14ms | ~200–500ms |
| GPU required | No | Yes (for production speed) |
| Auditability | Full — regex is human-readable | None — attention weights |
| Air-gap friendly | Yes | Requires model download |
| False positives on structured fields | Near zero | Occasional |
| Custom entity types | Add a regex | Requires labelled data + retraining |

For **structured financial identifiers** (IBANs, SSNs, credit cards), regex is strictly better than ML. The patterns follow ISO standards — there's nothing probabilistic to learn.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                     │
│                                                         │
│   ┌─────────────────┐      ┌──────────────────────┐    │
│   │   index.html    │      │   REST Client / SDK   │    │
│   │  (Vanilla JS)   │      │   (curl, Python, etc) │    │
│   └────────┬────────┘      └──────────┬───────────┘    │
└────────────┼──────────────────────────┼────────────────┘
             │ WebSocket                │ HTTP
             ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                         │
│                                                         │
│   ┌──────────────────┐   ┌───────────────────────────┐  │
│   │  /ws/process     │   │  POST /api/process        │  │
│   │  WebSocket       │   │  POST /api/process/batch  │  │
│   │  (streaming)     │   │  GET  /api/samples        │  │
│   └────────┬─────────┘   │  GET  /api/entities/types │  │
│            │              └──────────────┬────────────┘  │
│            └──────────────┬─────────────┘               │
│                           ▼                              │
│              ┌────────────────────────┐                  │
│              │    BankNEREngine       │                  │
│              │                        │                  │
│              │  ┌──────────────────┐  │                  │
│              │  │ Regex Compiler   │  │                  │
│              │  │ (17 patterns)    │  │                  │
│              │  └────────┬─────────┘  │                  │
│              │           │            │                  │
│              │  ┌────────▼─────────┐  │                  │
│              │  │ Context Scorer   │  │                  │
│              │  │ (keyword window) │  │                  │
│              │  └────────┬─────────┘  │                  │
│              │           │            │                  │
│              │  ┌────────▼─────────┐  │                  │
│              │  │ Deduplicator     │  │                  │
│              │  │ (overlap removal)│  │                  │
│              │  └────────┬─────────┘  │                  │
│              │           │            │                  │
│              │  ┌────────▼─────────┐  │                  │
│              │  │ Risk Scorer      │  │                  │
│              │  │ (sensitivity     │  │                  │
│              │  │  weighted score) │  │                  │
│              │  └──────────────────┘  │                  │
│              └────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## How the NER Engine Works

### 1. Pattern Compilation
At startup, `BankNEREngine` compiles 17+ regex patterns into `re.Pattern` objects once. Every subsequent document scan reuses the compiled patterns — no recompilation overhead.

### 2. Context-Aware Matching
Some patterns (like account numbers — any 8-18 digit sequence) are too broad on their own. The engine checks a ±120 character window around each match for context keywords:

```python
# Account number only fires if nearby context contains:
["account", "acct", "a/c", "bank account", "savings", "checking"]
```

If no context keyword is found, the confidence score is halved and the match is dropped below the threshold.

### 3. Overlap Deduplication
When multiple patterns match overlapping text (e.g. an IBAN being partially matched as an account number), the engine sorts by position and confidence, keeping only the highest-confidence non-overlapping match.

### 4. Sensitivity & Risk Scoring
Every entity type has a fixed sensitivity level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`). The document risk score is a weighted average:

```
CRITICAL = 1.0 weight
HIGH     = 0.6 weight
MEDIUM   = 0.3 weight
LOW      = 0.1 weight

Risk Score = (sum of weights / entity count) × 10, capped at 10
```

### 5. Masking
CRITICAL and HIGH entities are automatically masked for safe display:
- SSN `456-78-9012` → `*******012`
- IBAN `GB29NWBK...` → `GB29****`

The original text is preserved in the JSON response for downstream use.

---

## API Reference

### `POST /api/process`

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text", "document_type": "wire_transfer"}'
```

**Document types:** `generic`, `wire_transfer`, `insurance_claim`, `loan`, `kyc`, `trade_confirmation`

**Response:**
```json
{
  "entities": [
    {
      "text": "GB29NWBK60161331926819",
      "label": "IBAN",
      "start": 9,
      "end": 31,
      "confidence": 0.97,
      "sensitivity": "HIGH",
      "color": "#45B7D1",
      "masked": "GB29****",
      "description": "International Bank Account Number",
      "source": "rule"
    }
  ],
  "processing_time_ms": 0.28,
  "char_count": 312,
  "entity_counts": {"IBAN": 1, "SWIFT_BIC": 1},
  "document_type": "wire_transfer",
  "risk_score": 4.33
}
```

### `POST /api/process/batch`
Process up to 50 documents in one call. Returns per-document results plus aggregate timing.

### `WS /ws/process`
Real-time streaming. Send:
```json
{"action": "process", "text": "...", "document_type": "wire_transfer"}
```
Receive a stream of:
```json
{"action": "entity_found", "entity": {...}}
{"action": "processing_complete", "total_entities": 7, "processing_time_ms": 0.28}
```

### All Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Interactive UI |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/process` | Process single document |
| `POST` | `/api/process/batch` | Process up to 50 documents |
| `POST` | `/api/process/file` | Upload `.txt` file |
| `GET` | `/api/samples` | List built-in sample documents |
| `GET` | `/api/sample/{key}` | Get sample document text |
| `GET` | `/api/entities/types` | Full entity catalog with colors |
| `WS` | `/ws/process` | Real-time streaming WebSocket |
| `GET` | `/docs` | Swagger / OpenAPI UI |

---

## Quick Start

### Requirements
- Python 3.10+
- pip

### Install & Run

```bash
# Clone the repo
git clone https://github.com/ajaysingh0419/bankner.git
cd bankner

# Install dependencies
pip install -r requirements.txt

# Start the server
cd backend
python server.py

# Open the UI
open http://localhost:8000       # macOS
xdg-open http://localhost:8000  # Linux
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Server port |

---

## Project Structure

```
bankner/
├── backend/
│   ├── server.py                  # FastAPI app — all routes, WebSocket handler
│   ├── models/
│   │   └── ner_engine.py          # NER engine — patterns, scoring, masking
│   └── utils/
│       └── sample_docs.py         # 4 synthetic sample documents
├── frontend/
│   └── index.html                 # Complete UI — zero build step, zero dependencies
├── tests/
│   └── test_engine.py             # 14 unit tests + performance benchmark
├── screenshot.png
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
python tests/test_engine.py
```

```
 BankNER Test Suite
==================================================
  ✓ PASS  IBAN detection
  ✓ PASS  SSN detection
  ✓ PASS  PAN detection
  ✓ PASS  SWIFT detection
  ✓ PASS  Currency amount
  ✓ PASS  Credit card
  ✓ PASS  Policy ID
  ✓ PASS  Claim number
  ✓ PASS  Email detection
  ✓ PASS  EIN / Tax ID
  ✓ PASS  Account number with context
  ✓ PASS  Person with title
  ✓ PASS  Org detection
  ✓ PASS  Date detection

  14/14 tests passed
  Perf: 15,576 chars → avg 14.1ms per doc
```

---

## Performance

| Document Size | Processing Time | Throughput |
|---|---|---|
| ~100 chars (single sentence) | ~0.3ms | ~3,000 docs/sec |
| ~2,000 chars (standard form) | ~2ms | ~500 docs/sec |
| ~15,000 chars (large agreement) | ~14ms | ~70 docs/sec |

Single-threaded, single CPU core, Apple M-series. Scale horizontally with multiple Uvicorn workers for production load.

---

## Extending the Engine

### Add a new entity type

In `backend/models/ner_engine.py`:

```python
# 1. Add to EntityType enum
class EntityType(str, Enum):
    MY_NEW_ENTITY = "MY_NEW_ENTITY"

# 2. Add color, description, sensitivity
ENTITY_COLORS[EntityType.MY_NEW_ENTITY] = "#FF9900"
ENTITY_DESCRIPTIONS[EntityType.MY_NEW_ENTITY] = "My new entity type"
SENSITIVITY_LEVELS[EntityType.MY_NEW_ENTITY] = "HIGH"

# 3. Add pattern to PATTERNS list
PATTERNS.append({
    "label": EntityType.MY_NEW_ENTITY,
    "regex": r"\bMY-PATTERN-[0-9]{6}\b",
    "confidence": 0.92,
    "context_keywords": ["optional", "context", "words"],
})
```

That's it. No retraining, no data labelling, no model deployment.

### Add ML model on top

```python
# In BankNEREngine.__init__():
# Replace: self.nlp = spacy.blank("en")
# With:
self.nlp = spacy.load("en_core_web_trf")  # transformer model
# Rule-based patterns still run; ML handles unstructured entities
```

---

## Production Deployment Notes

- **Auth:** Add JWT or API key middleware to `server.py` using `fastapi.security`
- **HTTPS:** Put Uvicorn behind nginx with TLS termination
- **Scaling:** Run multiple workers: `uvicorn server:app --workers 4`
- **Air-gap:** No outbound network calls required — copy the repo and install from a local pip mirror
- **Audit log:** Add a logging middleware to record every API call with entity counts for compliance

---

## Roadmap

- [ ] PDF ingestion via `pdfplumber`
- [ ] Fine-tuned spaCy model for improved address and org detection
- [ ] JWT / API key authentication middleware
- [ ] Redaction mode — return document with entities replaced by `[REDACTED]`
- [ ] Confidence threshold configuration per entity type via environment variables
- [ ] Audit log persistence to SQLite or Postgres
- [ ] Docker image for one-command deployment
- [ ] Multi-language support (Hindi, Arabic, German financial documents)

---

## License

MIT — use it, fork it, sell it. Attribution appreciated but not required.

---

<div align="center">
Built with Python, FastAPI, spaCy, and zero cloud dependencies.
</div>
