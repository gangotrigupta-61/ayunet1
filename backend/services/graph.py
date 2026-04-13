from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = None

def get_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

async def warm_up():
    """Verify Neo4j is reachable."""
    try:
        d = get_driver()
        with d.session() as session:
            session.run("RETURN 1")
        print("[Neo4j] Warm-up ping successful")
    except Exception as e:
        print(f"[Neo4j] Warm-up failed: {e}")

# ─── Q1: Symptom-to-Diagnosis Multi-hop Traversal ───

def run_diagnose(symptoms: list[str]) -> dict:
    """Multi-hop traversal: Symptom -> HAS_SYMPTOM -> Disease, ranked by match count + weight."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            UNWIND $symptoms AS symptom_name
            MATCH (s:Symptom)<-[r:HAS_SYMPTOM]-(d:Disease)
            WHERE toLower(s.name) = toLower(symptom_name)
            WITH d, count(DISTINCT s) AS matched_count, sum(r.weight) AS total_weight,
                 collect(DISTINCT s.name) AS matched_symptoms
            RETURN d.disease_id AS disease_id,
                   d.name AS disease_name,
                   d.icd_code AS icd_code,
                   d.description AS description,
                   d.prevalence AS prevalence,
                   matched_count,
                   matched_symptoms,
                   total_weight,
                   toFloat(matched_count) / $symptom_count AS confidence_score
            ORDER BY confidence_score DESC, total_weight DESC
            LIMIT 5
        """, symptoms=symptoms, symptom_count=len(symptoms))

        diagnoses = []
        for record in result:
            diagnoses.append({
                "disease_id": record["disease_id"],
                "disease_name": record["disease_name"],
                "icd_code": record["icd_code"] or "",
                "description": record["description"] or "",
                "prevalence": record["prevalence"] or 0,
                "matched_count": record["matched_count"],
                "matched_symptoms": record["matched_symptoms"],
                "total_weight": record["total_weight"],
                "confidence_score": record["confidence_score"],
            })
        return {"diagnoses": diagnoses}

# ─── Q2: Drug Interaction Check ───

def run_drug_interactions(drugs: list[str]) -> dict:
    """Pattern matching: find INTERACTS_WITH edges between selected drugs."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            UNWIND $drugs AS drug1_name
            UNWIND $drugs AS drug2_name
            WITH drug1_name, drug2_name WHERE drug1_name < drug2_name
            MATCH (d1:Drug)-[r:INTERACTS_WITH]-(d2:Drug)
            WHERE toLower(d1.name) = toLower(drug1_name)
              AND toLower(d2.name) = toLower(drug2_name)
            RETURN d1.name AS drug1,
                   d2.name AS drug2,
                   r.severity AS severity,
                   r.mechanism AS mechanism,
                   r.clinical_note AS clinical_note
            ORDER BY CASE r.severity
                WHEN 'severe' THEN 1
                WHEN 'moderate' THEN 2
                ELSE 3
            END
        """, drugs=drugs)

        interactions = []
        for record in result:
            interactions.append({
                "drug1": record["drug1"],
                "drug2": record["drug2"],
                "severity": record["severity"] or "mild",
                "mechanism": record["mechanism"] or "",
                "clinical_note": record["clinical_note"] or "",
            })
        return {"interactions": interactions}

# ─── Q3: Treatment Pathway (Shortest Path) ───

def run_treatment_path(disease_name: str) -> dict:
    """Disease -> Specialist + Treatment -> Drug pathway."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            MATCH (d:Disease)-[r1:TREATED_BY]->(t:Treatment)-[r2:PRESCRIBED]->(drug:Drug)
            WHERE toLower(d.name) = toLower($disease_name)
            OPTIONAL MATCH (d)-[:REFERS_TO]->(sp:Specialist)
            RETURN d.name AS disease_name,
                   sp.name AS specialist_name,
                   sp.specialization AS specialization,
                   t.name AS treatment_name,
                   t.treatment_type AS treatment_type,
                   t.cost_tier AS cost_tier,
                   drug.name AS drug_name,
                   drug.drug_class AS drug_class,
                   r1.success_rate AS success_rate,
                   r1.accessibility_score AS accessibility_score,
                   r2.dosage AS dosage,
                   r2.duration AS duration
            ORDER BY r1.success_rate DESC
        """, disease_name=disease_name)

        pathways = []
        for record in result:
            pathways.append({
                "disease_name": record["disease_name"],
                "specialist_name": record["specialist_name"] or "General Physician",
                "specialization": record["specialization"] or "",
                "treatment_name": record["treatment_name"],
                "treatment_type": record["treatment_type"] or "",
                "cost_tier": record["cost_tier"] or "medium",
                "drug_name": record["drug_name"],
                "drug_class": record["drug_class"] or "",
                "success_rate": record["success_rate"] or 0.7,
                "accessibility_score": record["accessibility_score"] or 0.5,
                "dosage": record["dosage"] or "",
                "duration": record["duration"] or "",
            })
        return {"pathways": pathways}

# ─── Q4: Rare Disease Detection (4-hop deep) ───

def run_rare_diseases(symptoms: list[str]) -> dict:
    """4-hop deep traversal to find rare diseases sharing atypical symptoms."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            UNWIND $symptoms AS symptom_name
            MATCH (s:Symptom)<-[:HAS_SYMPTOM]-(d:Disease)
            WHERE toLower(s.name) = toLower(symptom_name)
              AND d.prevalence IS NOT NULL AND d.prevalence < 0.05
            WITH d, collect(DISTINCT s.name) AS matched_symptoms, count(DISTINCT s) AS match_count
            OPTIONAL MATCH (d)-[:REFERS_TO]->(sp:Specialist)
            OPTIONAL MATCH (d)-[:REQUIRES_TEST]->(lt:LabTest)
            RETURN d.disease_id AS disease_id,
                   d.name AS disease_name,
                   d.icd_code AS icd_code,
                   d.prevalence AS prevalence,
                   d.description AS description,
                   matched_symptoms,
                   match_count,
                   sp.name AS specialist_name,
                   collect(DISTINCT lt.name) AS recommended_tests
            ORDER BY match_count DESC, d.prevalence ASC
            LIMIT 5
        """, symptoms=symptoms)

        rare = []
        for record in result:
            rare.append({
                "disease_id": record["disease_id"],
                "disease_name": record["disease_name"],
                "icd_code": record["icd_code"] or "",
                "prevalence": record["prevalence"] or 0,
                "description": record["description"] or "",
                "matched_symptoms": record["matched_symptoms"],
                "match_count": record["match_count"],
                "specialist": record["specialist_name"] or "",
                "recommended_tests": record["recommended_tests"],
            })
        return {"rare_diseases": rare}

# ─── Q5: Comorbidity Risk Prediction (4-hop) ───

def run_comorbidity_risk(patient_id: str) -> dict:
    """
    4-hop traversal:
    Hop 1: Patient -> existing Disease (HAS_CONDITION)
    Hop 2: Disease -> RiskFactor (RISK_INCREASES)
    Hop 3: RiskFactor -> predicted Disease (ELEVATES)
    Hop 4: predicted Disease -> LabTest (REQUIRES_TEST) + check if patient completed it
    """
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            MATCH (p:Patient {patient_id: $patient_id})-[:HAS_CONDITION]->(existing:Disease)
            WITH p, collect(DISTINCT existing.name) AS existing_diseases,
                 collect(DISTINCT existing) AS existing_nodes
            UNWIND existing_nodes AS ed
            MATCH (ed)-[:RISK_INCREASES]->(rf:RiskFactor)
            WITH p, existing_diseases, collect(DISTINCT rf.name) AS risk_factors,
                 collect(DISTINCT rf) AS rf_nodes
            UNWIND rf_nodes AS rfn
            MATCH (rfn)-[el:ELEVATES]->(predicted:Disease)
            WHERE NOT predicted.name IN existing_diseases
            WITH p, existing_diseases, risk_factors,
                 predicted, rfn.name AS via_risk_factor, el.multiplier AS multiplier,
                 collect(DISTINCT predicted.name) AS predicted_names
            OPTIONAL MATCH (predicted)-[:REQUIRES_TEST]->(lt:LabTest)
            OPTIONAL MATCH (p)-[:HAS_COMPLETED_TEST]->(lt)
            WITH predicted.name AS predicted_disease,
                 via_risk_factor,
                 coalesce(multiplier, 1.0) AS risk_score,
                 lt.name AS required_test,
                 CASE WHEN (p)-[:HAS_COMPLETED_TEST]->(lt) THEN true ELSE false END AS test_completed,
                 existing_diseases, risk_factors
            RETURN existing_diseases,
                   risk_factors,
                   predicted_disease,
                   via_risk_factor,
                   risk_score,
                   required_test,
                   test_completed
            ORDER BY risk_score DESC
        """, patient_id=patient_id)

        existing_diseases = []
        risk_factors = []
        predicted_diseases = set()
        required_tests = set()
        predictions = []

        for record in result:
            if not existing_diseases:
                existing_diseases = record["existing_diseases"] or []
                risk_factors = record["risk_factors"] or []
            pred = record["predicted_disease"]
            if pred:
                predicted_diseases.add(pred)
                predictions.append({
                    "predicted_disease": pred,
                    "via_risk_factor": record["via_risk_factor"] or "",
                    "risk_score": record["risk_score"] or 1.0,
                    "required_test": record["required_test"] or "N/A",
                    "test_completed": record["test_completed"],
                })
            if record["required_test"]:
                required_tests.add(record["required_test"])

        return {
            "hop1_existing_diseases": existing_diseases,
            "hop2_risk_factors": risk_factors,
            "hop3_predicted_diseases": list(predicted_diseases),
            "hop4_required_tests": list(required_tests),
            "predictions": predictions,
        }

# ─── Q6: Disease PageRank (simulated via connectivity) ───

def run_pagerank() -> dict:
    """Rank diseases by graph connectivity (symptom links + treatment links + risk links).
    Neo4j Community doesn't have GDS PageRank, so we approximate via degree centrality.
    """
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            MATCH (d:Disease)
            OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
            WITH d, count(DISTINCT s) AS symptom_links
            OPTIONAL MATCH (d)-[:TREATED_BY]->(t:Treatment)
            WITH d, symptom_links, count(DISTINCT t) AS treatment_links
            OPTIONAL MATCH (d)-[:RISK_INCREASES]->(rf:RiskFactor)
            WITH d, symptom_links, treatment_links, count(DISTINCT rf) AS risk_links
            OPTIONAL MATCH (d)-[:REFERS_TO]->(sp:Specialist)
            WITH d, symptom_links, treatment_links, risk_links, count(DISTINCT sp) AS specialist_links
            WITH d,
                 symptom_links + treatment_links + risk_links + specialist_links AS total_degree,
                 symptom_links, treatment_links, risk_links
            RETURN d.disease_id AS disease_id,
                   d.name AS disease_name,
                   total_degree,
                   symptom_links,
                   treatment_links,
                   risk_links,
                   toFloat(total_degree) / 20.0 AS rank_score
            ORDER BY total_degree DESC
        """)

        rankings = {}
        for record in result:
            rankings[record["disease_id"]] = {
                "disease_name": record["disease_name"],
                "rank_score": record["rank_score"],
                "total_degree": record["total_degree"],
                "symptom_links": record["symptom_links"],
                "treatment_links": record["treatment_links"],
                "risk_links": record["risk_links"],
            }
        return {"rankings": rankings}

# ─── Q7: Patient Context (Multi-hop read) ───

def run_patient_context(patient_id: str) -> dict:
    """Full patient context: conditions, medications, symptoms, risk factors."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            MATCH (p:Patient {patient_id: $patient_id})
            OPTIONAL MATCH (p)-[hc:HAS_CONDITION]->(d:Disease)
            OPTIONAL MATCH (p)-[tm:TAKES_MEDICATION]->(drug:Drug)
            OPTIONAL MATCH (p)-[pw:PRESENTS_WITH]->(s:Symptom)
            OPTIONAL MATCH (p)-[:HAS_FOLLOWUP]->(fu:FollowUp)
            OPTIONAL MATCH (d)-[:HAS_PROTOCOL]->(proto:Protocol)
            RETURN p.patient_id AS patient_id,
                   p.name AS patient_name,
                   p.phone AS phone,
                   p.language AS language,
                   p.age AS age,
                   p.gender AS gender,
                   collect(DISTINCT {name: d.name, status: hc.status, diagnosed_date: hc.diagnosed_date}) AS conditions,
                   collect(DISTINCT {name: drug.name, dosage: tm.dosage}) AS medications,
                   collect(DISTINCT s.name) AS symptoms,
                   collect(DISTINCT {id: fu.followup_id, status: fu.status, scheduled_date: fu.scheduled_date, pain_score: fu.pain_score}) AS followups,
                   collect(DISTINCT {name: proto.name, followup_days: proto.followup_days}) AS protocols
        """, patient_id=patient_id)

        record = result.single()
        if not record:
            return {
                "patient_id": patient_id,
                "patient_name": "Unknown",
                "language": "en",
                "phone": "",
                "followup_day": 1,
            }

        # Determine followup_day from protocols
        followup_day = 1
        protocols = record["protocols"] or []
        for proto in protocols:
            if proto.get("followup_days"):
                try:
                    days = [int(x.strip()) for x in proto["followup_days"].split(",")]
                    if days:
                        followup_day = days[0]
                except (ValueError, AttributeError):
                    pass

        return {
            "patient_id": record["patient_id"],
            "patient_name": record["patient_name"] or "Patient",
            "phone": record["phone"] or "",
            "language": record["language"] or "en",
            "age": record["age"],
            "gender": record["gender"] or "",
            "conditions": [c for c in (record["conditions"] or []) if c.get("name")],
            "medications": [m for m in (record["medications"] or []) if m.get("name")],
            "symptoms": [s for s in (record["symptoms"] or []) if s],
            "followups": [f for f in (record["followups"] or []) if f.get("id")],
            "protocols": protocols,
            "followup_day": followup_day,
        }

# ─── Q8: Due Follow-ups ───

def run_due_followups() -> dict:
    """Find patients with follow-ups due today."""
    d = get_driver()
    with d.session() as session:
        result = session.run("""
            MATCH (p:Patient)-[hf:HAS_FOLLOWUP]->(fu:FollowUp)
            WHERE fu.status = 'pending'
              AND fu.scheduled_date <= toString(date())
            OPTIONAL MATCH (p)-[:HAS_CONDITION]->(d:Disease)
            RETURN p.patient_id AS patient_id,
                   p.name AS patient_name,
                   p.phone AS phone,
                   p.language AS language,
                   fu.followup_id AS followup_id,
                   fu.scheduled_date AS scheduled_date,
                   hf.linked_disease AS condition,
                   collect(DISTINCT d.name) AS conditions
            ORDER BY fu.scheduled_date ASC
        """)

        patients = []
        for record in result:
            conditions = [c for c in (record["conditions"] or []) if c]
            patients.append({
                "patient_id": record["patient_id"],
                "patient_name": record["patient_name"],
                "phone": record["phone"] or "",
                "language": record["language"] or "en",
                "followup_id": record["followup_id"],
                "scheduled_date": record["scheduled_date"],
                "condition": record["condition"] or (conditions[0] if conditions else "General"),
                "followup_day": 1,
            })
        return {"patients": patients}

# ─── Upsert Follow-up Data ───

def upsert_followup(patient_id: str, followup_id: str, data: dict):
    """Write follow-up response data back to Neo4j."""
    d = get_driver()
    with d.session() as session:
        session.run("""
            MATCH (p:Patient {patient_id: $patient_id})-[:HAS_FOLLOWUP]->(fu:FollowUp {followup_id: $followup_id})
            SET fu.status = $status,
                fu.pain_score = $pain_score,
                fu.took_medication = $took_medication,
                fu.new_symptoms = $new_symptoms,
                fu.risk_flag = $risk_flag
        """,
            patient_id=patient_id,
            followup_id=followup_id,
            status=data.get("status", "completed"),
            pain_score=data.get("pain_score", 0),
            took_medication=data.get("took_medication", False),
            new_symptoms=data.get("new_symptoms", ""),
            risk_flag=data.get("risk_flag", False),
        )

# ─── PageRank cache ───

_pagerank_cache: dict | None = None

def get_cached_pagerank() -> dict:
    global _pagerank_cache
    if _pagerank_cache is None:
        _pagerank_cache = run_pagerank()
    return _pagerank_cache

def refresh_pagerank():
    global _pagerank_cache
    _pagerank_cache = run_pagerank()
