"""
BankNER API Server
==================
FastAPI backend providing:
  - POST /api/process         — synchronous NER processing
  - POST /api/process/batch   — batch processing
  - WS  /ws/process           — real-time streaming NER
  - GET  /api/samples         — list sample documents
  - GET  /api/sample/{key}    — get sample document
  - GET  /api/entities/types  — entity type catalog
  - GET  /api/health          — health check
"""

import json
import time
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging

from models.ner_engine import get_engine, ENTITY_COLORS, ENTITY_DESCRIPTIONS, SENSITIVITY_LEVELS, EntityType
from utils.sample_docs import get_sample, list_samples, SAMPLE_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bankner")

app = FastAPI(
    title="BankNER API",
    description="Production-grade Named Entity Recognition for banking and insurance documents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload engine at startup
engine = None


@app.on_event("startup")
async def startup_event():
    global engine
    logger.info("Initialising BankNER engine...")
    engine = get_engine()
    logger.info("Engine ready.")


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class ProcessRequest(BaseModel):
    text: str
    document_type: Optional[str] = "generic"


class BatchProcessRequest(BaseModel):
    documents: List[ProcessRequest]


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "engine": "bankner-v1.0", "timestamp": time.time()}


@app.get("/api/entities/types")
async def entity_types():
    types = []
    for et in EntityType:
        types.append({
            "label": et.value,
            "description": ENTITY_DESCRIPTIONS.get(et, ""),
            "sensitivity": SENSITIVITY_LEVELS.get(et, "LOW"),
            "color": ENTITY_COLORS.get(et, "#CCCCCC"),
        })
    return {"entity_types": types}


@app.get("/api/samples")
async def samples():
    return {"samples": list_samples()}


@app.get("/api/sample/{key}")
async def sample(key: str):
    doc = get_sample(key)
    if not doc:
        raise HTTPException(status_code=404, detail="Sample not found")
    return doc


@app.post("/api/process")
async def process(req: ProcessRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(req.text) > 100_000:
        raise HTTPException(status_code=413, detail="Document too large (max 100k chars)")

    result = engine.process(req.text, req.document_type or "generic")
    return result.to_dict()


@app.post("/api/process/batch")
async def process_batch(req: BatchProcessRequest):
    if len(req.documents) > 50:
        raise HTTPException(status_code=400, detail="Batch limit is 50 documents")

    results = []
    total_start = time.perf_counter()
    for doc in req.documents:
        r = engine.process(doc.text, doc.document_type or "generic")
        results.append(r.to_dict())

    total_ms = (time.perf_counter() - total_start) * 1000
    return {
        "results": results,
        "total_documents": len(results),
        "total_processing_ms": round(total_ms, 2),
        "avg_ms_per_doc": round(total_ms / max(len(results), 1), 2),
    }


@app.post("/api/process/file")
async def process_file(file: UploadFile = File(...), document_type: str = "generic"):
    if file.content_type not in ("text/plain", "application/octet-stream", "text/csv"):
        # Only plain text in this version; PDF support requires pdfplumber (installable)
        raise HTTPException(status_code=415, detail="Only plain text files supported in this version")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    result = engine.process(text, document_type)
    return result.to_dict()


# ---------------------------------------------------------------------------
# WebSocket — real-time streaming
# ---------------------------------------------------------------------------

@app.websocket("/ws/process")
async def ws_process(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            action = data.get("action", "process")

            if action == "ping":
                await websocket.send_json({"action": "pong"})
                continue

            if action == "process":
                text = data.get("text", "")
                doc_type = data.get("document_type", "generic")

                if not text.strip():
                    await websocket.send_json({"action": "error", "message": "Empty text"})
                    continue

                # Send acknowledgement immediately
                await websocket.send_json({
                    "action": "processing_start",
                    "char_count": len(text),
                    "document_type": doc_type,
                })

                # For large docs, simulate streaming by processing in chunks
                # In practice this gives the UI immediate feedback
                await asyncio.sleep(0)  # yield to event loop

                result = engine.process(text, doc_type)

                # Stream entities one by one for real-time UI updates
                for entity in result.entities:
                    await websocket.send_json({
                        "action": "entity_found",
                        "entity": entity.to_dict(),
                    })
                    await asyncio.sleep(0.02)  # 20ms between entities for visual effect

                await websocket.send_json({
                    "action": "processing_complete",
                    "processing_time_ms": result.processing_time_ms,
                    "char_count": result.char_count,
                    "entity_counts": result.entity_counts,
                    "document_type": result.document_type,
                    "risk_score": result.risk_score,
                    "total_entities": len(result.entities),
                })

            elif action == "load_sample":
                key = data.get("key", "wire_transfer")
                doc = get_sample(key)
                await websocket.send_json({
                    "action": "sample_loaded",
                    "key": key,
                    "title": doc["title"],
                    "text": doc["text"],
                    "document_type": doc["type"],
                })

            else:
                await websocket.send_json({"action": "error", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"action": "error", "message": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
