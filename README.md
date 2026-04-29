# BankNER — Production NER Platform for Banking & Insurance

Real-time Named Entity Recognition for financial documents. Self-contained, no cloud dependencies, designed for on-premises deployment in regulated environments.

---

## What it detects

| Entity | Examples | Sensitivity |
|---|---|---|
| `ACCOUNT_NUMBER` | `4521890123456789` | HIGH |
| `IBAN` | `GB29NWBK60161331926819` | HIGH |
| `SWIFT_BIC` | `NWBKGB2L` | MEDIUM |
| `ROUTING_NUMBER` | `021000021` | HIGH |
| `SSN` | `456-78-9012` | CRITICAL |
| `CREDIT_CARD` | `4532015112830366` | CRITICAL |
| `PAN` | `BKQPS8832P` | HIGH |
| `TAX_ID / EIN` | `47-1234567` | HIGH |
| `POLICY_ID` | `POLHLT-2023-447821` | MEDIUM |
| `CLAIM_NUMBER` | `CLM-2024-089234` | LOW |
| `CURRENCY_AMOUNT` | `$2,500,000.00` | LOW |
| `PERSON` | `Dr. Sarah Mitchell` | MEDIUM |
| `ORG` | `NatWest Bank plc` | LOW |
| `EMAIL` | `user@bank.com` | MEDIUM |
| `PHONE` | `+1-212-555-0187` | MEDIUM |
| `DATE` | `15 March 2024` | LOW |
| `LOAN_ID` | `LN-2024-087654` | MEDIUM |

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
# Open http://localhost:8000
```

## API

```bash
# Process a document
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Account: 9876543210, IBAN: GB29NWBK60161331926819", "document_type": "wire_transfer"}'

# Batch processing
curl -X POST http://localhost:8000/api/process/batch \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"text": "..."}, {"text": "..."}]}'

# API docs
open http://localhost:8000/docs
```

## WebSocket (real-time)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/process');
ws.send(JSON.stringify({
  action: 'process',
  text: 'Your document here',
  document_type: 'wire_transfer'
}));
// Receive entities streamed one-by-one as they are found
```

## Run tests

```bash
python tests/test_engine.py
```

---

## Architecture

```
bankner/
├── main.py                  # Unified entry point
├── backend/
│   ├── server.py            # FastAPI + WebSocket server
│   ├── models/
│   │   └── ner_engine.py    # Core NER engine (rule-based, auditable)
│   └── utils/
│       └── sample_docs.py   # Synthetic sample documents
├── frontend/
│   └── index.html           # Interactive UI (single file, no build step)
└── tests/
    └── test_engine.py       # Unit + perf tests
```

## Design Decisions

**Why rule-based over ML models?**
- Deterministic and auditable — compliance teams can inspect and sign off on every pattern
- No model download required → works in air-gapped environments
- Zero false positives on structured fields (IBAN, SSN, PAN follow strict formats)
- Faster: <5ms for typical documents vs 200-500ms for transformer inference
- Easily extensible: add patterns in `ner_engine.py` without retraining

**Why spaCy as the base?**
- Production-grade NLP pipeline infrastructure
- Supports adding ML models later (plug `en_core_web_trf` for entity boosting)
- Apache 2.0 license, bank-friendly

**Extending with ML**
To add a trained NER model on top of rule-based detection, install a spaCy model and call `nlp.add_pipe("ner")` in `BankNEREngine.__init__`. The engine merges both layers.

## Honest notes on "70% time reduction" claims

This system reduces **manual entity extraction time** significantly for structured documents. Actual savings depend on:
- Your current process (fully manual vs semi-automated)
- Document complexity and variability
- Integration effort with downstream systems

Benchmark against your actual workflow before making client promises.
