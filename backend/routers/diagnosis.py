import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from schemas.models import AnalyzeRequest, DrugCheckRequest, TreatmentPathRequest, RareDiseaseRequest
from services import graph as graph_service
from services import nlp as nlp_service

router = APIRouter(prefix="/api", tags=["diagnosis"])


@router.post("/analyze")
async def analyze_symptoms(req: AnalyzeRequest):
    """Full pipeline: text -> Groq extract -> Q1 diagnosis -> Q6 PageRank weighting."""
    # Extract symptoms via Groq
    extracted = await nlp_service.extract_symptoms(req.text)
    symptoms = extracted.get("symptoms", [])
    language = extracted.get("language", "en")

    if not symptoms:
        return {"diagnoses": [], "extracted": extracted, "message": "No symptoms detected"}

    # Run Q1 + Q4 + Q6 in parallel
    loop = asyncio.get_event_loop()
    diagnose_task = loop.run_in_executor(None, graph_service.run_diagnose, symptoms)
    rare_task = loop.run_in_executor(None, graph_service.run_rare_diseases, symptoms)

    diagnose_result, rare_result = await asyncio.gather(diagnose_task, rare_task)
    pagerank = graph_service.get_cached_pagerank()

    return {
        "extracted": extracted,
        "diagnoses": diagnose_result,
        "rare_diseases": rare_result,
        "pagerank": pagerank,
        "language": language,
    }


@router.post("/drug-check")
async def check_drug_interactions(req: DrugCheckRequest):
    """Q2: Check drug interactions."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, graph_service.run_drug_interactions, req.drugs)
    return {"interactions": result, "drugs": req.drugs}


@router.post("/treatment-path")
async def find_treatment_path(req: TreatmentPathRequest):
    """Q3: Find treatment pathway."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, graph_service.run_treatment_path, req.disease)
    return {"pathway": result, "disease": req.disease}


@router.post("/rare-disease")
async def detect_rare_diseases(req: RareDiseaseRequest):
    """Q4: Rare disease detection (4-hop)."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, graph_service.run_rare_diseases, req.symptoms)
    return {"rare_diseases": result}


@router.get("/patient/{patient_id}/risks")
async def get_patient_risks(patient_id: str):
    """Q5 + Q7: Comorbidity risk + full patient context in parallel."""
    loop = asyncio.get_event_loop()
    risk_task = loop.run_in_executor(None, graph_service.run_comorbidity_risk, patient_id)
    context_task = loop.run_in_executor(None, graph_service.run_patient_context, patient_id)
    risk_result, context_result = await asyncio.gather(risk_task, context_task)
    return {"risks": risk_result, "context": context_result, "patient_id": patient_id}


@router.get("/disease-rankings")
async def get_disease_rankings():
    """Q6: PageRank disease rankings (cached)."""
    return {"rankings": graph_service.get_cached_pagerank()}


@router.get("/patient/{patient_id}/context")
async def get_patient_context(patient_id: str):
    """Q7: Full patient context for call script generation."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, graph_service.run_patient_context, patient_id)
    return {"context": result}


@router.get("/graph/overview")
async def get_graph_overview():
    """Schema metadata for visualization."""
    return {
        "vertex_types": [
            {"name": "Patient", "shape": "ellipse", "color": "#ffffff", "border": "#1e40af"},
            {"name": "Symptom", "shape": "round-rectangle", "color": "#3b82f6"},
            {"name": "Disease", "shape": "hexagon", "color": "#ef4444"},
            {"name": "Drug", "shape": "round-rectangle", "color": "#22c55e"},
            {"name": "Specialist", "shape": "diamond", "color": "#a855f7"},
            {"name": "Treatment", "shape": "rectangle", "color": "#f97316"},
            {"name": "RiskFactor", "shape": "triangle", "color": "#eab308"},
            {"name": "LabTest", "shape": "ellipse", "color": "#06b6d4"},
            {"name": "Protocol", "shape": "rectangle", "color": "#6b7280"},
            {"name": "FollowUp", "shape": "round-rectangle", "color": "#ec4899"},
        ],
        "edge_types": [
            "HAS_SYMPTOM", "PRESENTS_WITH", "HAS_CONDITION", "TAKES_MEDICATION",
            "TREATED_BY", "PRESCRIBED", "INTERACTS_WITH", "RISK_INCREASES",
            "ELEVATES", "REQUIRES_TEST", "HAS_COMPLETED_TEST", "REFERS_TO",
            "HAS_PROTOCOL", "HAS_FOLLOWUP", "CAUSES_SIDE_EFFECT",
        ],
    }
