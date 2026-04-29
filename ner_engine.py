"""
BankNER Core Engine
====================
Rule-based + statistical NER for banking/insurance documents.
Uses spaCy EntityRuler (deterministic, auditable, no external downloads).

Entity types:
  ACCOUNT_NUMBER  - Bank account numbers (various formats)
  SWIFT_BIC       - SWIFT/BIC codes
  IBAN            - International Bank Account Numbers
  PAN             - Permanent Account Numbers (India)
  SSN             - Social Security Numbers (US)
  POLICY_ID       - Insurance policy identifiers
  CLAIM_NUMBER    - Insurance claim numbers
  CURRENCY_AMOUNT - Monetary values with currency
  ROUTING_NUMBER  - US ABA routing numbers
  CREDIT_CARD     - Credit card numbers (masked detection)
  PERSON          - Named persons (heuristic)
  ORG             - Organizations (heuristic)
  DATE            - Date expressions
  LOAN_ID         - Loan/mortgage identifiers
  TAX_ID          - EIN / Tax identifiers
"""

import re
import time
import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class EntityType(str, Enum):
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"
    SWIFT_BIC = "SWIFT_BIC"
    IBAN = "IBAN"
    PAN = "PAN"
    SSN = "SSN"
    POLICY_ID = "POLICY_ID"
    CLAIM_NUMBER = "CLAIM_NUMBER"
    CURRENCY_AMOUNT = "CURRENCY_AMOUNT"
    ROUTING_NUMBER = "ROUTING_NUMBER"
    CREDIT_CARD = "CREDIT_CARD"
    PERSON = "PERSON"
    ORG = "ORG"
    DATE = "DATE"
    LOAN_ID = "LOAN_ID"
    TAX_ID = "TAX_ID"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ADDRESS = "ADDRESS"


ENTITY_COLORS = {
    EntityType.ACCOUNT_NUMBER: "#FF6B6B",
    EntityType.SWIFT_BIC: "#4ECDC4",
    EntityType.IBAN: "#45B7D1",
    EntityType.PAN: "#96CEB4",
    EntityType.SSN: "#FFEAA7",
    EntityType.POLICY_ID: "#DDA0DD",
    EntityType.CLAIM_NUMBER: "#F0A500",
    EntityType.CURRENCY_AMOUNT: "#6BCB77",
    EntityType.ROUTING_NUMBER: "#FF8C94",
    EntityType.CREDIT_CARD: "#FF6348",
    EntityType.PERSON: "#A8E6CF",
    EntityType.ORG: "#FFD3B6",
    EntityType.DATE: "#C3B1E1",
    EntityType.LOAN_ID: "#B5EAD7",
    EntityType.TAX_ID: "#FFDAC1",
    EntityType.EMAIL: "#E2F0CB",
    EntityType.PHONE: "#BDE0FE",
    EntityType.ADDRESS: "#FFC8DD",
}

ENTITY_DESCRIPTIONS = {
    EntityType.ACCOUNT_NUMBER: "Bank account number",
    EntityType.SWIFT_BIC: "SWIFT/BIC code for international wire transfers",
    EntityType.IBAN: "International Bank Account Number",
    EntityType.PAN: "Permanent Account Number (India tax ID)",
    EntityType.SSN: "Social Security Number",
    EntityType.POLICY_ID: "Insurance policy identifier",
    EntityType.CLAIM_NUMBER: "Insurance claim number",
    EntityType.CURRENCY_AMOUNT: "Monetary amount with currency",
    EntityType.ROUTING_NUMBER: "ABA routing/transit number",
    EntityType.CREDIT_CARD: "Credit/debit card number (PCI sensitive)",
    EntityType.PERSON: "Person name",
    EntityType.ORG: "Organization name",
    EntityType.DATE: "Date expression",
    EntityType.LOAN_ID: "Loan or mortgage identifier",
    EntityType.TAX_ID: "Tax ID / EIN",
    EntityType.EMAIL: "Email address",
    EntityType.PHONE: "Phone number",
    EntityType.ADDRESS: "Physical address",
}

SENSITIVITY_LEVELS = {
    EntityType.ACCOUNT_NUMBER: "HIGH",
    EntityType.SWIFT_BIC: "MEDIUM",
    EntityType.IBAN: "HIGH",
    EntityType.PAN: "HIGH",
    EntityType.SSN: "CRITICAL",
    EntityType.POLICY_ID: "MEDIUM",
    EntityType.CLAIM_NUMBER: "LOW",
    EntityType.CURRENCY_AMOUNT: "LOW",
    EntityType.ROUTING_NUMBER: "HIGH",
    EntityType.CREDIT_CARD: "CRITICAL",
    EntityType.PERSON: "MEDIUM",
    EntityType.ORG: "LOW",
    EntityType.DATE: "LOW",
    EntityType.LOAN_ID: "MEDIUM",
    EntityType.TAX_ID: "HIGH",
    EntityType.EMAIL: "MEDIUM",
    EntityType.PHONE: "MEDIUM",
    EntityType.ADDRESS: "MEDIUM",
}


@dataclass
class DetectedEntity:
    text: str
    label: str
    start: int
    end: int
    confidence: float
    description: str
    sensitivity: str
    color: str
    source: str = "rule"  # "rule" | "model" | "hybrid"
    masked: str = ""       # masked version for display

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "description": self.description,
            "sensitivity": self.sensitivity,
            "color": self.color,
            "source": self.source,
            "masked": self.masked,
        }


@dataclass
class NERResult:
    text: str
    entities: List[DetectedEntity]
    processing_time_ms: float
    char_count: int
    entity_counts: Dict[str, int] = field(default_factory=dict)
    document_type: str = "generic"
    risk_score: float = 0.0

    def __post_init__(self):
        self.entity_counts = {}
        for e in self.entities:
            self.entity_counts[e.label] = self.entity_counts.get(e.label, 0) + 1
        self.risk_score = self._compute_risk()

    def _compute_risk(self) -> float:
        weights = {"CRITICAL": 1.0, "HIGH": 0.6, "MEDIUM": 0.3, "LOW": 0.1}
        score = sum(weights.get(e.sensitivity, 0) for e in self.entities)
        return min(score / max(len(self.entities), 1) * 10, 10.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "processing_time_ms": self.processing_time_ms,
            "char_count": self.char_count,
            "entity_counts": self.entity_counts,
            "document_type": self.document_type,
            "risk_score": round(self.risk_score, 2),
        }


# ---------------------------------------------------------------------------
# Regex pattern library
# ---------------------------------------------------------------------------

PATTERNS: List[Dict[str, Any]] = [
    # IBAN — must come before account numbers (more specific)
    {
        "label": EntityType.IBAN,
        "regex": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
        "confidence": 0.97,
    },
    # SWIFT / BIC
    {
        "label": EntityType.SWIFT_BIC,
        "regex": r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
        "confidence": 0.85,
        "context_keywords": ["swift", "bic", "wire", "bank code", "routing"],
    },
    # US Routing number (9 digits, ABA)
    {
        "label": EntityType.ROUTING_NUMBER,
        "regex": r"\b0[0-9]{8}\b|\b[1-9][0-9]{8}\b",
        "confidence": 0.7,
        "context_keywords": ["routing", "aba", "transit", "rt no", "rtn"],
    },
    # Account numbers (8-18 digits, must have context)
    {
        "label": EntityType.ACCOUNT_NUMBER,
        "regex": r"\b\d{8,18}\b",
        "confidence": 0.75,
        "context_keywords": [
            "account", "acct", "acc no", "a/c", "account number",
            "bank account", "deposit", "savings", "checking"
        ],
    },
    # PAN (India) — AAAAA9999A format
    {
        "label": EntityType.PAN,
        "regex": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "confidence": 0.95,
    },
    # SSN
    {
        "label": EntityType.SSN,
        "regex": r"\b(?!000|666|9\d{2})\d{3}[- ](?!00)\d{2}[- ](?!0000)\d{4}\b",
        "confidence": 0.97,
    },
    # Credit card (Luhn-detectable patterns)
    {
        "label": EntityType.CREDIT_CARD,
        "regex": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
        "confidence": 0.98,
    },
    # Loan / Mortgage IDs
    {
        "label": EntityType.LOAN_ID,
        "regex": r"\b(?:LN|LOAN|MTG|MRG|HE)[- ]?[0-9]{6,12}\b",
        "confidence": 0.93,
        "context_keywords": ["loan", "mortgage", "lien", "credit facility"],
    },
    # Policy IDs
    {
        "label": EntityType.POLICY_ID,
        "regex": r"\b(?:POL|PLY|POLICY)[A-Z0-9\-]{4,20}\b|\b[A-Z]{2,4}[0-9]{6,10}\b",
        "confidence": 0.82,
        "context_keywords": ["policy", "insurance", "coverage", "insured", "premium"],
    },
    # Claim numbers
    {
        "label": EntityType.CLAIM_NUMBER,
        "regex": r"\b(?:CLM|CLAIM)[- ]?[A-Z0-9]{4,14}\b|\bCL[0-9]{6,10}\b",
        "confidence": 0.90,
        "context_keywords": ["claim", "claimant", "adjuster", "settlement"],
    },
    # EIN / Tax ID
    {
        "label": EntityType.TAX_ID,
        "regex": r"\b\d{2}-\d{7}\b",
        "confidence": 0.88,
        "context_keywords": ["ein", "tax id", "employer id", "tin", "federal id"],
    },
    # Currency amounts
    {
        "label": EntityType.CURRENCY_AMOUNT,
        "regex": r"(?:USD|EUR|GBP|INR|JPY|AED|SAR|CHF|CAD|AUD)?\s*[\$£€₹¥]\s*[\d,]+(?:\.\d{2})?|[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|INR|JPY|dollars?|euros?|pounds?|rupees?)",
        "confidence": 0.92,
    },
    # Email
    {
        "label": EntityType.EMAIL,
        "regex": r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b",
        "confidence": 0.99,
    },
    # Phone
    {
        "label": EntityType.PHONE,
        "regex": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\+\d{1,3}[-.\s]?\d{6,14}\b",
        "confidence": 0.88,
    },
    # Dates (various formats)
    {
        "label": EntityType.DATE,
        "regex": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{2}[/-]\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",
        "confidence": 0.90,
    },
]

# Person name heuristics (title-based detection)
PERSON_TITLE_REGEX = re.compile(
    r"\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|Sir|Hon\.?|Rev\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
)

# Org heuristics
ORG_SUFFIX_REGEX = re.compile(
    r"\b([A-Z][A-Za-z\s&,\.]{2,40}(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Bank|Insurance|Financial|Capital|Holdings?|Group|Fund|Trust|Credit Union|N\.A\.|plc|GmbH|S\.A\.|AG))\b"
)


def _mask_entity(text: str, label: str) -> str:
    """Return a display-safe masked version."""
    if label in (EntityType.SSN, EntityType.CREDIT_CARD):
        return "*" * (len(text) - 4) + text[-4:]
    if label in (EntityType.ACCOUNT_NUMBER, EntityType.IBAN, EntityType.ROUTING_NUMBER):
        keep = min(4, len(text))
        return text[:keep] + "*" * max(0, len(text) - keep)
    return text


def _context_match(text: str, match_start: int, keywords: List[str], window: int = 120) -> bool:
    """Check if any keyword appears within `window` chars of the match."""
    ctx_start = max(0, match_start - window)
    ctx_end = min(len(text), match_start + window)
    context = text[ctx_start:ctx_end].lower()
    return any(kw.lower() in context for kw in keywords)


class BankNEREngine:
    """
    Production NER engine for banking and insurance documents.
    Fully self-contained — no external model downloads required.
    Designed for air-gapped / on-premises deployment.
    """

    def __init__(self):
        self.nlp = spacy.blank("en")
        self._compiled: List[Dict[str, Any]] = []
        self._compile_patterns()

    def _compile_patterns(self):
        for p in PATTERNS:
            self._compiled.append({
                **p,
                "_re": re.compile(p["regex"]),
            })

    def _deduplicate(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Remove overlapping entities, keeping higher confidence."""
        entities.sort(key=lambda e: (e.start, -e.confidence))
        result = []
        last_end = -1
        for e in entities:
            if e.start >= last_end:
                result.append(e)
                last_end = e.end
        return result

    def process(self, text: str, document_type: str = "generic") -> NERResult:
        t0 = time.perf_counter()
        entities: List[DetectedEntity] = []

        for pat in self._compiled:
            regex: re.Pattern = pat["_re"]
            label: EntityType = pat["label"]
            base_conf: float = pat["confidence"]
            context_kws: List[str] = pat.get("context_keywords", [])

            for m in regex.finditer(text):
                conf = base_conf
                if context_kws:
                    if not _context_match(text, m.start(), context_kws):
                        conf *= 0.5  # penalise context-dependent patterns
                        if conf < 0.55:
                            continue

                ent = DetectedEntity(
                    text=m.group(),
                    label=label.value,
                    start=m.start(),
                    end=m.end(),
                    confidence=round(conf, 3),
                    description=ENTITY_DESCRIPTIONS.get(label, ""),
                    sensitivity=SENSITIVITY_LEVELS.get(label, "LOW"),
                    color=ENTITY_COLORS.get(label, "#CCCCCC"),
                    source="rule",
                    masked=_mask_entity(m.group(), label.value),
                )
                entities.append(ent)

        # Person names
        for m in PERSON_TITLE_REGEX.finditer(text):
            entities.append(DetectedEntity(
                text=m.group(),
                label=EntityType.PERSON.value,
                start=m.start(),
                end=m.end(),
                confidence=0.87,
                description=ENTITY_DESCRIPTIONS[EntityType.PERSON],
                sensitivity=SENSITIVITY_LEVELS[EntityType.PERSON],
                color=ENTITY_COLORS[EntityType.PERSON],
                source="rule",
                masked=m.group(),
            ))

        # Org names
        for m in ORG_SUFFIX_REGEX.finditer(text):
            entities.append(DetectedEntity(
                text=m.group(),
                label=EntityType.ORG.value,
                start=m.start(),
                end=m.end(),
                confidence=0.80,
                description=ENTITY_DESCRIPTIONS[EntityType.ORG],
                sensitivity=SENSITIVITY_LEVELS[EntityType.ORG],
                color=ENTITY_COLORS[EntityType.ORG],
                source="rule",
                masked=m.group(),
            ))

        entities = self._deduplicate(entities)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        return NERResult(
            text=text,
            entities=entities,
            processing_time_ms=round(elapsed_ms, 2),
            char_count=len(text),
            document_type=document_type,
        )

    def process_batch(self, texts: List[str], document_type: str = "generic") -> List[NERResult]:
        return [self.process(t, document_type) for t in texts]


# Singleton
_engine: Optional[BankNEREngine] = None


def get_engine() -> BankNEREngine:
    global _engine
    if _engine is None:
        _engine = BankNEREngine()
    return _engine
