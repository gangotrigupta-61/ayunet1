"""
AyuNet Seed Data Script
Seeds Neo4j with comprehensive medical data for demo.
Run: cd backend && python scripts/seed_data.py
"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()


def main():
    print("[Seed] Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.run("RETURN 1")
    print("[Seed] Connected!\n")

    with driver.session() as session:
        # ─── SYMPTOMS (50+) ───
        print("[Seed] Upserting symptoms...")
        symptoms = [
            ("fever", "fever", "general"), ("headache", "headache", "neurological"),
            ("cough", "cough", "respiratory"), ("fatigue", "fatigue", "general"),
            ("body_aches", "body aches", "musculoskeletal"), ("nausea", "nausea", "gastrointestinal"),
            ("vomiting", "vomiting", "gastrointestinal"), ("diarrhea", "diarrhea", "gastrointestinal"),
            ("abdominal_pain", "abdominal pain", "gastrointestinal"),
            ("chest_pain", "chest pain", "cardiovascular"),
            ("shortness_of_breath", "shortness of breath", "respiratory"),
            ("joint_pain", "joint pain", "musculoskeletal"),
            ("rash", "rash", "dermatological"), ("sore_throat", "sore throat", "respiratory"),
            ("runny_nose", "runny nose", "respiratory"), ("chills", "chills", "general"),
            ("sweating", "sweating", "general"), ("weight_loss", "weight loss", "general"),
            ("weight_gain", "weight gain", "general"), ("dizziness", "dizziness", "neurological"),
            ("blurred_vision", "blurred vision", "ophthalmological"),
            ("frequent_urination", "frequent urination", "urological"),
            ("increased_thirst", "increased thirst", "general"),
            ("muscle_weakness", "muscle weakness", "musculoskeletal"),
            ("numbness", "numbness", "neurological"), ("tingling", "tingling", "neurological"),
            ("back_pain", "back pain", "musculoskeletal"),
            ("neck_stiffness", "neck stiffness", "musculoskeletal"),
            ("swollen_lymph_nodes", "swollen lymph nodes", "immunological"),
            ("night_sweats", "night sweats", "general"),
            ("loss_of_appetite", "loss of appetite", "general"),
            ("bleeding_gums", "bleeding gums", "hematological"),
            ("bruising", "bruising", "hematological"),
            ("yellow_skin", "yellow skin (jaundice)", "hepatological"),
            ("dark_urine", "dark urine", "urological"),
            ("pale_stool", "pale stool", "gastrointestinal"),
            ("swelling_legs", "swelling in legs", "cardiovascular"),
            ("palpitations", "palpitations", "cardiovascular"),
            ("wheezing", "wheezing", "respiratory"),
            ("blood_in_sputum", "blood in sputum", "respiratory"),
            ("painful_urination", "painful urination", "urological"),
            ("high_blood_pressure", "high blood pressure", "cardiovascular"),
            ("low_blood_pressure", "low blood pressure", "cardiovascular"),
            ("confusion", "confusion", "neurological"),
            ("memory_loss", "memory loss", "neurological"),
            ("anxiety", "anxiety", "psychiatric"), ("depression_symptom", "depressed mood", "psychiatric"),
            ("insomnia", "insomnia", "psychiatric"),
            ("skin_itching", "skin itching", "dermatological"),
            ("hair_loss", "hair loss", "dermatological"),
            ("dry_mouth", "dry mouth", "general"),
            ("excessive_hunger", "excessive hunger", "general"),
        ]
        for sid, name, cat in symptoms:
            session.run(
                "MERGE (s:Symptom {symptom_id: $sid}) SET s.name = $name, s.category = $cat",
                sid=sid, name=name, cat=cat,
            )
        print(f"  -> {len(symptoms)} symptoms")

        # ─── DISEASES (22) ───
        print("[Seed] Upserting diseases...")
        diseases = [
            ("dengue", "Dengue Fever", "A90", 0.12, "Mosquito-borne viral infection causing high fever and body pain"),
            ("malaria", "Malaria", "B50", 0.08, "Parasitic infection transmitted by mosquitoes"),
            ("typhoid", "Typhoid Fever", "A01.0", 0.06, "Bacterial infection from contaminated food/water"),
            ("diabetes_t2", "Type 2 Diabetes", "E11", 0.15, "Chronic metabolic disorder with insulin resistance"),
            ("hypertension", "Hypertension", "I10", 0.20, "Chronically elevated blood pressure"),
            ("cad", "Coronary Artery Disease", "I25.1", 0.10, "Narrowing of coronary arteries"),
            ("pneumonia", "Pneumonia", "J18", 0.09, "Lung infection causing inflammation"),
            ("tuberculosis", "Tuberculosis", "A15", 0.04, "Bacterial infection primarily affecting the lungs"),
            ("asthma", "Asthma", "J45", 0.11, "Chronic airway inflammation"),
            ("ckd", "Chronic Kidney Disease", "N18", 0.07, "Progressive loss of kidney function"),
            ("rheumatoid", "Rheumatoid Arthritis", "M06.9", 0.03, "Autoimmune disorder attacking joints"),
            ("depression", "Depression", "F32", 0.13, "Mental health disorder with persistent sadness"),
            ("anemia", "Anemia", "D64.9", 0.14, "Reduced red blood cells or hemoglobin"),
            ("gastritis", "Gastritis", "K29", 0.10, "Inflammation of stomach lining"),
            ("hepatitis_b", "Hepatitis B", "B16", 0.02, "Viral liver infection"),
            ("lupus", "Systemic Lupus Erythematosus", "M32", 0.01, "Autoimmune disease affecting multiple organs"),
            ("hypothyroid", "Hypothyroidism", "E03.9", 0.08, "Underactive thyroid gland"),
            ("dvt", "Deep Vein Thrombosis", "I82", 0.02, "Blood clot in deep veins"),
            ("gout", "Gout", "M10", 0.04, "Inflammatory arthritis from uric acid crystals"),
            ("migraine", "Migraine", "G43", 0.12, "Severe recurring headache disorder"),
            ("chikungunya", "Chikungunya", "A92.0", 0.03, "Mosquito-borne viral infection with joint pain"),
            ("celiac", "Celiac Disease", "K90.0", 0.01, "Autoimmune disorder triggered by gluten"),
        ]
        for did, name, icd, prev, desc in diseases:
            session.run(
                "MERGE (d:Disease {disease_id: $did}) "
                "SET d.name = $name, d.icd_code = $icd, d.prevalence = $prev, d.description = $desc",
                did=did, name=name, icd=icd, prev=prev, desc=desc,
            )
        print(f"  -> {len(diseases)} diseases")

        # ─── DISEASE-SYMPTOM EDGES ───
        print("[Seed] Creating disease-symptom edges...")
        disease_symptoms = [
            # Dengue
            ("dengue", "fever", 0.95), ("dengue", "headache", 0.85), ("dengue", "body_aches", 0.90),
            ("dengue", "rash", 0.60), ("dengue", "nausea", 0.70), ("dengue", "fatigue", 0.80),
            ("dengue", "bleeding_gums", 0.30), ("dengue", "joint_pain", 0.75), ("dengue", "chills", 0.65),
            # Malaria
            ("malaria", "fever", 0.95), ("malaria", "chills", 0.90), ("malaria", "sweating", 0.85),
            ("malaria", "headache", 0.80), ("malaria", "nausea", 0.65), ("malaria", "vomiting", 0.55),
            ("malaria", "body_aches", 0.70), ("malaria", "fatigue", 0.75),
            # Typhoid
            ("typhoid", "fever", 0.95), ("typhoid", "headache", 0.75), ("typhoid", "abdominal_pain", 0.80),
            ("typhoid", "diarrhea", 0.60), ("typhoid", "loss_of_appetite", 0.70), ("typhoid", "fatigue", 0.65),
            ("typhoid", "rash", 0.30),
            # Type 2 Diabetes
            ("diabetes_t2", "frequent_urination", 0.85), ("diabetes_t2", "increased_thirst", 0.80),
            ("diabetes_t2", "fatigue", 0.75), ("diabetes_t2", "blurred_vision", 0.60),
            ("diabetes_t2", "weight_loss", 0.55), ("diabetes_t2", "numbness", 0.50),
            ("diabetes_t2", "excessive_hunger", 0.65), ("diabetes_t2", "dry_mouth", 0.50),
            # Hypertension
            ("hypertension", "headache", 0.60), ("hypertension", "dizziness", 0.55),
            ("hypertension", "chest_pain", 0.40), ("hypertension", "shortness_of_breath", 0.45),
            ("hypertension", "palpitations", 0.50), ("hypertension", "blurred_vision", 0.35),
            ("hypertension", "high_blood_pressure", 0.95),
            # CAD
            ("cad", "chest_pain", 0.90), ("cad", "shortness_of_breath", 0.80),
            ("cad", "fatigue", 0.65), ("cad", "palpitations", 0.60),
            ("cad", "swelling_legs", 0.45), ("cad", "dizziness", 0.50),
            # Pneumonia
            ("pneumonia", "cough", 0.90), ("pneumonia", "fever", 0.85),
            ("pneumonia", "shortness_of_breath", 0.80), ("pneumonia", "chest_pain", 0.65),
            ("pneumonia", "fatigue", 0.60), ("pneumonia", "chills", 0.55),
            # TB
            ("tuberculosis", "cough", 0.90), ("tuberculosis", "blood_in_sputum", 0.60),
            ("tuberculosis", "night_sweats", 0.75), ("tuberculosis", "weight_loss", 0.70),
            ("tuberculosis", "fever", 0.65), ("tuberculosis", "fatigue", 0.70),
            ("tuberculosis", "loss_of_appetite", 0.60),
            # Asthma
            ("asthma", "wheezing", 0.90), ("asthma", "shortness_of_breath", 0.85),
            ("asthma", "cough", 0.75), ("asthma", "chest_pain", 0.40),
            # CKD
            ("ckd", "fatigue", 0.80), ("ckd", "swelling_legs", 0.75),
            ("ckd", "frequent_urination", 0.65), ("ckd", "nausea", 0.55),
            ("ckd", "loss_of_appetite", 0.60), ("ckd", "muscle_weakness", 0.50),
            # RA
            ("rheumatoid", "joint_pain", 0.95), ("rheumatoid", "fatigue", 0.70),
            ("rheumatoid", "muscle_weakness", 0.55), ("rheumatoid", "numbness", 0.35),
            # Depression
            ("depression", "depression_symptom", 0.95), ("depression", "insomnia", 0.75),
            ("depression", "fatigue", 0.80), ("depression", "loss_of_appetite", 0.65),
            ("depression", "anxiety", 0.70), ("depression", "memory_loss", 0.40),
            ("depression", "weight_gain", 0.45),
            # Anemia
            ("anemia", "fatigue", 0.90), ("anemia", "dizziness", 0.70),
            ("anemia", "shortness_of_breath", 0.55), ("anemia", "pale_stool", 0.30),
            ("anemia", "hair_loss", 0.40), ("anemia", "muscle_weakness", 0.50),
            # Gastritis
            ("gastritis", "abdominal_pain", 0.90), ("gastritis", "nausea", 0.75),
            ("gastritis", "vomiting", 0.55), ("gastritis", "loss_of_appetite", 0.60),
            # Hepatitis B
            ("hepatitis_b", "yellow_skin", 0.80), ("hepatitis_b", "fatigue", 0.70),
            ("hepatitis_b", "abdominal_pain", 0.65), ("hepatitis_b", "dark_urine", 0.60),
            ("hepatitis_b", "nausea", 0.55), ("hepatitis_b", "loss_of_appetite", 0.50),
            # Lupus (rare)
            ("lupus", "rash", 0.85), ("lupus", "joint_pain", 0.80),
            ("lupus", "fatigue", 0.75), ("lupus", "fever", 0.50),
            ("lupus", "hair_loss", 0.45), ("lupus", "muscle_weakness", 0.40),
            # Hypothyroid
            ("hypothyroid", "fatigue", 0.85), ("hypothyroid", "weight_gain", 0.75),
            ("hypothyroid", "dry_mouth", 0.50), ("hypothyroid", "hair_loss", 0.60),
            ("hypothyroid", "depression_symptom", 0.45), ("hypothyroid", "muscle_weakness", 0.55),
            # DVT (rare)
            ("dvt", "swelling_legs", 0.90), ("dvt", "chest_pain", 0.40),
            ("dvt", "shortness_of_breath", 0.35),
            # Gout
            ("gout", "joint_pain", 0.95), ("gout", "rash", 0.30), ("gout", "fever", 0.25),
            # Migraine
            ("migraine", "headache", 0.95), ("migraine", "nausea", 0.60),
            ("migraine", "blurred_vision", 0.45), ("migraine", "dizziness", 0.40),
            # Chikungunya
            ("chikungunya", "fever", 0.90), ("chikungunya", "joint_pain", 0.95),
            ("chikungunya", "rash", 0.55), ("chikungunya", "headache", 0.60),
            ("chikungunya", "fatigue", 0.65),
            # Celiac (rare)
            ("celiac", "diarrhea", 0.80), ("celiac", "abdominal_pain", 0.75),
            ("celiac", "weight_loss", 0.60), ("celiac", "fatigue", 0.65),
            ("celiac", "rash", 0.40), ("celiac", "joint_pain", 0.30),
        ]
        for did, sid, weight in disease_symptoms:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (s:Symptom {symptom_id: $sid}) "
                "MERGE (d)-[r:HAS_SYMPTOM]->(s) SET r.weight = $weight",
                did=did, sid=sid, weight=weight,
            )
        print(f"  -> {len(disease_symptoms)} disease-symptom edges")

        # ─── DRUGS (28) ───
        print("[Seed] Upserting drugs...")
        drugs = [
            ("metformin", "Metformin", "biguanide", "nausea, diarrhea"),
            ("warfarin", "Warfarin", "anticoagulant", "bleeding, bruising"),
            ("paracetamol", "Paracetamol", "analgesic", "liver damage (overdose)"),
            ("aspirin", "Aspirin", "NSAID/antiplatelet", "GI bleeding, stomach upset"),
            ("ibuprofen", "Ibuprofen", "NSAID", "GI upset, kidney risk"),
            ("amoxicillin", "Amoxicillin", "antibiotic", "diarrhea, rash"),
            ("omeprazole", "Omeprazole", "PPI", "headache, nausea"),
            ("amlodipine", "Amlodipine", "calcium channel blocker", "swelling, dizziness"),
            ("simvastatin", "Simvastatin", "statin", "muscle pain, liver issues"),
            ("clopidogrel", "Clopidogrel", "antiplatelet", "bleeding, bruising"),
            ("fluoxetine", "Fluoxetine", "SSRI", "nausea, insomnia"),
            ("sertraline", "Sertraline", "SSRI", "nausea, dizziness"),
            ("rifampicin", "Rifampicin", "antibiotic", "liver toxicity, orange urine"),
            ("lisinopril", "Lisinopril", "ACE inhibitor", "cough, dizziness"),
            ("phenytoin", "Phenytoin", "anticonvulsant", "gum overgrowth, dizziness"),
            ("isoniazid", "Isoniazid", "antibiotic", "liver toxicity, neuropathy"),
            ("prednisolone", "Prednisolone", "corticosteroid", "weight gain, mood changes"),
            ("atenolol", "Atenolol", "beta blocker", "fatigue, cold hands"),
            ("losartan", "Losartan", "ARB", "dizziness, hyperkalemia"),
            ("diclofenac", "Diclofenac", "NSAID", "GI bleeding, kidney risk"),
            ("insulin_glargine", "Insulin Glargine", "insulin", "hypoglycemia"),
            ("azithromycin", "Azithromycin", "antibiotic", "diarrhea, nausea"),
            ("hydroxychloroquine", "Hydroxychloroquine", "antimalarial/immunomod", "retinal toxicity"),
            ("allopurinol", "Allopurinol", "xanthine oxidase inhibitor", "rash, liver issues"),
            ("salbutamol", "Salbutamol", "bronchodilator", "tremor, tachycardia"),
            ("chloroquine", "Chloroquine", "antimalarial", "nausea, vision changes"),
            ("methotrexate", "Methotrexate", "DMARD", "liver toxicity, nausea"),
            ("levothyroxine", "Levothyroxine", "thyroid hormone", "palpitations, anxiety"),
        ]
        for drug_id, name, drug_class, side_effects in drugs:
            session.run(
                "MERGE (d:Drug {drug_id: $did}) "
                "SET d.name = $name, d.drug_class = $cls, d.common_side_effects = $se",
                did=drug_id, name=name, cls=drug_class, se=side_effects,
            )
        print(f"  -> {len(drugs)} drugs")

        # ─── DRUG INTERACTIONS ───
        print("[Seed] Creating drug interactions...")
        interactions = [
            ("warfarin", "aspirin", "severe", "Increased anticoagulant effect and bleeding risk",
             "Avoid combination. If necessary, monitor INR closely and watch for signs of bleeding."),
            ("warfarin", "ibuprofen", "severe", "NSAIDs inhibit platelet function and may cause GI bleeding",
             "Use paracetamol instead of NSAIDs when possible."),
            ("warfarin", "rifampicin", "severe", "Rifampicin induces CYP enzymes, reducing warfarin efficacy",
             "May need to double warfarin dose. Monitor INR weekly."),
            ("metformin", "prednisolone", "moderate", "Corticosteroids increase blood glucose",
             "Monitor blood sugar more frequently. May need insulin temporarily."),
            ("simvastatin", "amlodipine", "moderate", "Increased risk of myopathy/rhabdomyolysis",
             "Limit simvastatin to 20mg/day when combined with amlodipine."),
            ("clopidogrel", "omeprazole", "moderate", "Omeprazole reduces clopidogrel activation via CYP2C19",
             "Use pantoprazole instead of omeprazole."),
            ("fluoxetine", "sertraline", "severe", "Serotonin syndrome risk with dual SSRIs",
             "Never combine two SSRIs. Taper one before starting another."),
            ("lisinopril", "losartan", "moderate", "Dual RAAS blockade increases hyperkalemia and renal failure risk",
             "Avoid combination. Use one agent only."),
            ("aspirin", "clopidogrel", "moderate", "Dual antiplatelet increases bleeding risk",
             "Acceptable post-stent for limited duration under specialist supervision."),
            ("isoniazid", "rifampicin", "moderate", "Combined hepatotoxicity risk",
             "Standard TB regimen but monitor LFTs monthly."),
            ("phenytoin", "fluoxetine", "moderate", "Fluoxetine inhibits phenytoin metabolism",
             "Monitor phenytoin levels. May need dose reduction."),
            ("diclofenac", "aspirin", "moderate", "Increased GI bleeding risk and reduced aspirin cardioprotection",
             "Avoid combination. Use paracetamol for pain."),
        ]
        for d1, d2, sev, mech, note in interactions:
            session.run(
                "MATCH (a:Drug {drug_id: $d1}), (b:Drug {drug_id: $d2}) "
                "MERGE (a)-[r:INTERACTS_WITH]-(b) "
                "SET r.severity = $sev, r.mechanism = $mech, r.clinical_note = $note",
                d1=d1, d2=d2, sev=sev, mech=mech, note=note,
            )
        print(f"  -> {len(interactions)} drug interactions")

        # ─── SPECIALISTS (12) ───
        print("[Seed] Upserting specialists...")
        specialists = [
            ("general_physician", "Dr. General Physician", "General Medicine"),
            ("cardiologist", "Dr. Cardiologist", "Cardiology"),
            ("endocrinologist", "Dr. Endocrinologist", "Endocrinology"),
            ("pulmonologist", "Dr. Pulmonologist", "Pulmonology"),
            ("nephrologist", "Dr. Nephrologist", "Nephrology"),
            ("rheumatologist", "Dr. Rheumatologist", "Rheumatology"),
            ("psychiatrist", "Dr. Psychiatrist", "Psychiatry"),
            ("hematologist", "Dr. Hematologist", "Hematology"),
            ("gastroenterologist", "Dr. Gastroenterologist", "Gastroenterology"),
            ("hepatologist", "Dr. Hepatologist", "Hepatology"),
            ("dermatologist", "Dr. Dermatologist", "Dermatology"),
            ("neurologist", "Dr. Neurologist", "Neurology"),
        ]
        for sid, name, spec in specialists:
            session.run(
                "MERGE (s:Specialist {specialist_id: $sid}) SET s.name = $name, s.specialization = $spec",
                sid=sid, name=name, spec=spec,
            )
        print(f"  -> {len(specialists)} specialists")

        # ─── DISEASE → SPECIALIST REFERRALS ───
        print("[Seed] Creating disease-specialist referrals...")
        referrals = [
            ("dengue", "general_physician"), ("malaria", "general_physician"),
            ("typhoid", "general_physician"), ("diabetes_t2", "endocrinologist"),
            ("hypertension", "cardiologist"), ("cad", "cardiologist"),
            ("pneumonia", "pulmonologist"), ("tuberculosis", "pulmonologist"),
            ("asthma", "pulmonologist"), ("ckd", "nephrologist"),
            ("rheumatoid", "rheumatologist"), ("depression", "psychiatrist"),
            ("anemia", "hematologist"), ("gastritis", "gastroenterologist"),
            ("hepatitis_b", "hepatologist"), ("lupus", "rheumatologist"),
            ("hypothyroid", "endocrinologist"), ("dvt", "cardiologist"),
            ("gout", "rheumatologist"), ("migraine", "neurologist"),
            ("chikungunya", "general_physician"), ("celiac", "gastroenterologist"),
        ]
        for did, sid in referrals:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (s:Specialist {specialist_id: $sid}) "
                "MERGE (d)-[:REFERS_TO]->(s)",
                did=did, sid=sid,
            )
        print(f"  -> {len(referrals)} referral edges")

        # ─── TREATMENTS (12) ───
        print("[Seed] Upserting treatments...")
        treatments = [
            ("treat_antibiotic", "Antibiotic Therapy", "medication", "low"),
            ("treat_antiviral", "Antiviral Supportive Care", "supportive", "low"),
            ("treat_insulin", "Insulin Therapy", "medication", "medium"),
            ("treat_oral_hypoglycemic", "Oral Hypoglycemic Therapy", "medication", "low"),
            ("treat_antihypertensive", "Antihypertensive Therapy", "medication", "low"),
            ("treat_stent", "Coronary Stenting", "procedure", "high"),
            ("treat_bronchodilator", "Bronchodilator Therapy", "medication", "low"),
            ("treat_dots", "DOTS TB Treatment", "medication", "low"),
            ("treat_dialysis", "Hemodialysis", "procedure", "high"),
            ("treat_dmard", "DMARD Therapy", "medication", "medium"),
            ("treat_ssri", "SSRI Antidepressant Therapy", "medication", "low"),
            ("treat_ppi", "PPI Therapy", "medication", "low"),
        ]
        for tid, name, ttype, cost in treatments:
            session.run(
                "MERGE (t:Treatment {treatment_id: $tid}) "
                "SET t.name = $name, t.treatment_type = $ttype, t.cost_tier = $cost",
                tid=tid, name=name, ttype=ttype, cost=cost,
            )
        print(f"  -> {len(treatments)} treatments")

        # ─── DISEASE → TREATMENT EDGES ───
        print("[Seed] Creating disease-treatment edges...")
        disease_treatments = [
            ("dengue", "treat_antiviral", 0.85, 0.9),
            ("malaria", "treat_antiviral", 0.90, 0.85),
            ("typhoid", "treat_antibiotic", 0.90, 0.9),
            ("diabetes_t2", "treat_oral_hypoglycemic", 0.80, 0.95),
            ("diabetes_t2", "treat_insulin", 0.85, 0.7),
            ("hypertension", "treat_antihypertensive", 0.85, 0.95),
            ("cad", "treat_antihypertensive", 0.70, 0.9),
            ("cad", "treat_stent", 0.90, 0.5),
            ("pneumonia", "treat_antibiotic", 0.85, 0.9),
            ("tuberculosis", "treat_dots", 0.90, 0.85),
            ("asthma", "treat_bronchodilator", 0.85, 0.95),
            ("ckd", "treat_dialysis", 0.75, 0.4),
            ("rheumatoid", "treat_dmard", 0.70, 0.6),
            ("depression", "treat_ssri", 0.75, 0.9),
            ("gastritis", "treat_ppi", 0.85, 0.95),
        ]
        for did, tid, success, access in disease_treatments:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (t:Treatment {treatment_id: $tid}) "
                "MERGE (d)-[r:TREATED_BY]->(t) SET r.success_rate = $success, r.accessibility_score = $access",
                did=did, tid=tid, success=success, access=access,
            )
        print(f"  -> {len(disease_treatments)} disease-treatment edges")

        # ─── TREATMENT → DRUG PRESCRIPTIONS ───
        print("[Seed] Creating treatment-drug prescriptions...")
        prescriptions = [
            ("treat_antiviral", "paracetamol", "500mg 3x/day", "5-7 days"),
            ("treat_antibiotic", "amoxicillin", "500mg 3x/day", "7-10 days"),
            ("treat_antibiotic", "azithromycin", "500mg 1x/day", "3-5 days"),
            ("treat_oral_hypoglycemic", "metformin", "500mg 2x/day", "ongoing"),
            ("treat_insulin", "insulin_glargine", "10-40 units/day", "ongoing"),
            ("treat_antihypertensive", "amlodipine", "5mg 1x/day", "ongoing"),
            ("treat_antihypertensive", "lisinopril", "10mg 1x/day", "ongoing"),
            ("treat_antihypertensive", "atenolol", "50mg 1x/day", "ongoing"),
            ("treat_stent", "clopidogrel", "75mg 1x/day", "12 months"),
            ("treat_stent", "aspirin", "75mg 1x/day", "lifelong"),
            ("treat_bronchodilator", "salbutamol", "2 puffs PRN", "as needed"),
            ("treat_dots", "isoniazid", "300mg 1x/day", "6 months"),
            ("treat_dots", "rifampicin", "600mg 1x/day", "6 months"),
            ("treat_dmard", "methotrexate", "15mg 1x/week", "ongoing"),
            ("treat_dmard", "hydroxychloroquine", "200mg 2x/day", "ongoing"),
            ("treat_ssri", "fluoxetine", "20mg 1x/day", "6-12 months"),
            ("treat_ssri", "sertraline", "50mg 1x/day", "6-12 months"),
            ("treat_ppi", "omeprazole", "20mg 1x/day", "4-8 weeks"),
        ]
        for tid, did, dosage, duration in prescriptions:
            session.run(
                "MATCH (t:Treatment {treatment_id: $tid}), (d:Drug {drug_id: $did}) "
                "MERGE (t)-[r:PRESCRIBED]->(d) SET r.dosage = $dosage, r.duration = $duration",
                tid=tid, did=did, dosage=dosage, duration=duration,
            )
        print(f"  -> {len(prescriptions)} treatment-drug edges")

        # ─── RISK FACTORS (10) ───
        print("[Seed] Upserting risk factors...")
        risk_factors = [
            ("rf_obesity", "Obesity", "lifestyle"),
            ("rf_smoking", "Smoking", "lifestyle"),
            ("rf_sedentary", "Sedentary Lifestyle", "lifestyle"),
            ("rf_family_diabetes", "Family History of Diabetes", "genetic"),
            ("rf_family_heart", "Family History of Heart Disease", "genetic"),
            ("rf_high_cholesterol", "High Cholesterol", "metabolic"),
            ("rf_alcohol", "Heavy Alcohol Use", "lifestyle"),
            ("rf_stress", "Chronic Stress", "lifestyle"),
            ("rf_age_over_50", "Age Over 50", "demographic"),
            ("rf_insulin_resistance", "Insulin Resistance", "metabolic"),
        ]
        for rid, name, cat in risk_factors:
            session.run(
                "MERGE (r:RiskFactor {risk_factor_id: $rid}) SET r.name = $name, r.category = $cat",
                rid=rid, name=name, cat=cat,
            )
        print(f"  -> {len(risk_factors)} risk factors")

        # ─── DISEASE → RISK_FACTOR EDGES ───
        print("[Seed] Creating disease-risk edges...")
        disease_risks = [
            ("diabetes_t2", "rf_obesity"), ("diabetes_t2", "rf_sedentary"),
            ("diabetes_t2", "rf_family_diabetes"), ("diabetes_t2", "rf_insulin_resistance"),
            ("hypertension", "rf_obesity"), ("hypertension", "rf_smoking"),
            ("hypertension", "rf_stress"), ("hypertension", "rf_sedentary"),
            ("cad", "rf_smoking"), ("cad", "rf_high_cholesterol"),
            ("cad", "rf_family_heart"), ("cad", "rf_obesity"),
            ("ckd", "rf_obesity"), ("depression", "rf_stress"),
            ("depression", "rf_alcohol"),
        ]
        for did, rid in disease_risks:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (r:RiskFactor {risk_factor_id: $rid}) "
                "MERGE (d)-[:RISK_INCREASES]->(r)",
                did=did, rid=rid,
            )
        print(f"  -> {len(disease_risks)} disease-risk edges")

        # ─── RISK_FACTOR → DISEASE ELEVATION EDGES ───
        print("[Seed] Creating risk-elevation edges...")
        elevations = [
            ("rf_obesity", "cad", 2.1), ("rf_obesity", "hypertension", 1.8),
            ("rf_obesity", "diabetes_t2", 2.5), ("rf_obesity", "ckd", 1.5),
            ("rf_smoking", "cad", 2.5), ("rf_smoking", "hypertension", 1.6),
            ("rf_smoking", "pneumonia", 1.4),
            ("rf_sedentary", "diabetes_t2", 1.7), ("rf_sedentary", "cad", 1.5),
            ("rf_family_diabetes", "diabetes_t2", 2.8),
            ("rf_family_heart", "cad", 2.3), ("rf_family_heart", "hypertension", 1.8),
            ("rf_high_cholesterol", "cad", 2.4), ("rf_high_cholesterol", "dvt", 1.6),
            ("rf_alcohol", "hepatitis_b", 1.9), ("rf_alcohol", "gastritis", 1.7),
            ("rf_stress", "hypertension", 1.5), ("rf_stress", "depression", 2.0),
            ("rf_insulin_resistance", "diabetes_t2", 3.0), ("rf_insulin_resistance", "cad", 1.8),
            ("rf_age_over_50", "cad", 1.6), ("rf_age_over_50", "ckd", 1.4),
        ]
        for rid, did, mult in elevations:
            session.run(
                "MATCH (r:RiskFactor {risk_factor_id: $rid}), (d:Disease {disease_id: $did}) "
                "MERGE (r)-[e:ELEVATES]->(d) SET e.multiplier = $mult",
                rid=rid, did=did, mult=mult,
            )
        print(f"  -> {len(elevations)} risk-elevation edges")

        # ─── LAB TESTS (14) ───
        print("[Seed] Upserting lab tests...")
        lab_tests = [
            ("lt_cbc", "Complete Blood Count (CBC)", "blood"),
            ("lt_hba1c", "HbA1c", "blood"), ("lt_fbs", "Fasting Blood Sugar", "blood"),
            ("lt_lipid", "Lipid Profile", "blood"), ("lt_ecg", "ECG", "cardiac"),
            ("lt_echo", "Echocardiogram", "cardiac"), ("lt_creatinine", "Serum Creatinine", "blood"),
            ("lt_lft", "Liver Function Test", "blood"), ("lt_xray", "Chest X-Ray", "imaging"),
            ("lt_sputum", "Sputum Culture", "microbiology"),
            ("lt_thyroid", "Thyroid Profile (TSH/T3/T4)", "blood"),
            ("lt_rf", "Rheumatoid Factor", "blood"),
            ("lt_hbsag", "HBsAg Test", "blood"),
            ("lt_uric_acid", "Serum Uric Acid", "blood"),
        ]
        for tid, name, ttype in lab_tests:
            session.run(
                "MERGE (l:LabTest {lab_test_id: $tid}) SET l.name = $name, l.test_type = $ttype",
                tid=tid, name=name, ttype=ttype,
            )
        print(f"  -> {len(lab_tests)} lab tests")

        # ─── DISEASE → LAB TEST EDGES ───
        print("[Seed] Creating disease-labtest edges...")
        disease_tests = [
            ("dengue", "lt_cbc"), ("malaria", "lt_cbc"),
            ("diabetes_t2", "lt_hba1c"), ("diabetes_t2", "lt_fbs"),
            ("hypertension", "lt_ecg"), ("hypertension", "lt_lipid"),
            ("cad", "lt_ecg"), ("cad", "lt_echo"), ("cad", "lt_lipid"),
            ("pneumonia", "lt_xray"), ("tuberculosis", "lt_xray"), ("tuberculosis", "lt_sputum"),
            ("ckd", "lt_creatinine"), ("hepatitis_b", "lt_lft"), ("hepatitis_b", "lt_hbsag"),
            ("anemia", "lt_cbc"), ("hypothyroid", "lt_thyroid"),
            ("rheumatoid", "lt_rf"), ("gout", "lt_uric_acid"),
        ]
        for did, tid in disease_tests:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (l:LabTest {lab_test_id: $tid}) "
                "MERGE (d)-[:REQUIRES_TEST]->(l)",
                did=did, tid=tid,
            )
        print(f"  -> {len(disease_tests)} disease-labtest edges")

        # ─── PROTOCOLS (3) ───
        print("[Seed] Upserting protocols...")
        protocols = [
            ("proto_surgery", "Post-Surgery Follow-up", "1,3,7,14,30",
             "How is your pain? Are you taking medication? Any new symptoms?"),
            ("proto_chronic", "Chronic Disease Management", "7,14,30,60,90",
             "How are you feeling? Blood sugar readings? Any side effects?"),
            ("proto_acute", "Acute Illness Recovery", "1,3,7",
             "Is the fever gone? Any new symptoms? Are you eating well?"),
        ]
        for pid, name, days, questions in protocols:
            session.run(
                "MERGE (p:Protocol {protocol_id: $pid}) "
                "SET p.name = $name, p.followup_days = $days, p.questions_template = $questions",
                pid=pid, name=name, days=days, questions=questions,
            )
        print(f"  -> {len(protocols)} protocols")

        # ─── DISEASE → PROTOCOL EDGES ───
        disease_protocols = [
            ("dengue", "proto_acute"), ("malaria", "proto_acute"),
            ("typhoid", "proto_acute"), ("diabetes_t2", "proto_chronic"),
            ("hypertension", "proto_chronic"), ("cad", "proto_surgery"),
            ("asthma", "proto_chronic"), ("ckd", "proto_chronic"),
            ("rheumatoid", "proto_chronic"), ("hypothyroid", "proto_chronic"),
            ("depression", "proto_chronic"), ("lupus", "proto_chronic"),
            ("gastritis", "proto_acute"), ("chikungunya", "proto_acute"),
        ]
        for did, pid in disease_protocols:
            session.run(
                "MATCH (d:Disease {disease_id: $did}), (p:Protocol {protocol_id: $pid}) "
                "MERGE (d)-[:HAS_PROTOCOL]->(p)",
                did=did, pid=pid,
            )
        print(f"  -> {len(disease_protocols)} disease-protocol edges")

        # ─── PATIENTS (10) ───
        print("[Seed] Upserting patients...")
        # All phones set to demo number for testing
        DEMO_PHONE = "+917985582272"
        patients = [
            ("priya", "Priya", DEMO_PHONE, "hi", 32, "female"),
            ("karthik", "Karthik", DEMO_PHONE, "ta", 45, "male"),
            ("ananya", "Ananya", DEMO_PHONE, "te", 28, "female"),
            ("rahul", "Rahul", DEMO_PHONE, "en", 55, "male"),
            ("meera", "Meera", DEMO_PHONE, "bn", 35, "female"),
            ("aryan", "Aryan", DEMO_PHONE, "hi", 21, "male"),
            ("suresh", "Suresh", DEMO_PHONE, "hi", 62, "male"),
            ("lakshmi", "Lakshmi", DEMO_PHONE, "ta", 48, "female"),
            ("dev", "Dev", DEMO_PHONE, "en", 38, "male"),
            ("fatima", "Fatima", DEMO_PHONE, "hi", 29, "female"),
        ]
        for pid, name, phone, lang, age, gender in patients:
            session.run(
                "MERGE (p:Patient {patient_id: $pid}) "
                "SET p.name = $name, p.phone = $phone, p.language = $lang, p.age = $age, p.gender = $gender",
                pid=pid, name=name, phone=phone, lang=lang, age=age, gender=gender,
            )
        print(f"  -> {len(patients)} patients")

        # ─── PATIENT → DISEASE (HAS_CONDITION) ───
        print("[Seed] Creating patient-condition edges...")
        patient_conditions = [
            ("priya", "dengue", "2024-03-10", "active"),
            ("priya", "diabetes_t2", "2023-01-15", "chronic"),
            ("karthik", "cad", "2024-02-20", "post-surgery"),
            ("karthik", "hypertension", "2022-06-01", "chronic"),
            ("ananya", "lupus", "2024-03-01", "active"),
            ("ananya", "anemia", "2024-02-15", "active"),
            ("rahul", "hypertension", "2020-01-01", "chronic"),
            ("rahul", "diabetes_t2", "2021-06-15", "chronic"),
            ("rahul", "cad", "2023-09-01", "chronic"),
            ("meera", "hypothyroid", "2023-03-10", "chronic"),
            ("meera", "depression", "2023-08-01", "active"),
            ("meera", "anemia", "2023-09-15", "active"),
            ("aryan", "dengue", TODAY, "active"),
            # Suresh: 62M, Diabetes + CKD + Hypertension — complex chronic
            ("suresh", "diabetes_t2", "2018-05-01", "chronic"),
            ("suresh", "ckd", "2022-11-15", "chronic"),
            ("suresh", "hypertension", "2019-02-01", "chronic"),
            # Lakshmi: 48F, Asthma + Gastritis — respiratory + GI
            ("lakshmi", "asthma", "2020-06-01", "chronic"),
            ("lakshmi", "gastritis", "2024-01-20", "active"),
            # Dev: 38M, Typhoid — acute recovery
            ("dev", "typhoid", TODAY, "active"),
            # Fatima: 29F, Rheumatoid Arthritis + Migraine
            ("fatima", "rheumatoid", "2023-07-01", "active"),
            ("fatima", "migraine", "2022-01-15", "chronic"),
        ]
        for pid, did, diag_date, status in patient_conditions:
            session.run(
                "MATCH (p:Patient {patient_id: $pid}), (d:Disease {disease_id: $did}) "
                "MERGE (p)-[r:HAS_CONDITION]->(d) SET r.diagnosed_date = $dd, r.status = $status",
                pid=pid, did=did, dd=diag_date, status=status,
            )
        print(f"  -> {len(patient_conditions)} patient-condition edges")

        # ─── PATIENT → DRUG (TAKES_MEDICATION) ───
        print("[Seed] Creating patient-medication edges...")
        patient_meds = [
            # Priya — Dengue + Diabetes
            ("priya", "paracetamol", "500mg 3x/day (after meals)", "2024-03-10"),
            ("priya", "metformin", "500mg 2x/day (morning & night)", "2023-01-15"),
            # Karthik — CAD post-surgery + Hypertension
            ("karthik", "clopidogrel", "75mg 1x/day (morning)", "2024-02-20"),
            ("karthik", "aspirin", "75mg 1x/day (after lunch)", "2024-02-20"),
            ("karthik", "atenolol", "50mg 1x/day (morning)", "2022-06-01"),
            ("karthik", "simvastatin", "20mg 1x/day (night)", "2024-02-20"),
            # Ananya — Lupus + Anemia
            ("ananya", "hydroxychloroquine", "200mg 2x/day (morning & night)", "2024-03-01"),
            ("ananya", "prednisolone", "10mg 1x/day (morning after breakfast)", "2024-03-01"),
            # Rahul — Hypertension + Diabetes + CAD
            ("rahul", "metformin", "1000mg 2x/day (morning & night)", "2021-06-15"),
            ("rahul", "amlodipine", "5mg 1x/day (morning)", "2020-01-01"),
            ("rahul", "simvastatin", "20mg 1x/day (night)", "2023-09-01"),
            ("rahul", "aspirin", "75mg 1x/day (after lunch)", "2023-09-01"),
            # Meera — Hypothyroid + Depression + Anemia
            ("meera", "levothyroxine", "50mcg 1x/day (empty stomach, 30 min before breakfast)", "2023-03-10"),
            ("meera", "sertraline", "50mg 1x/day (night)", "2023-08-01"),
            # Aryan — Dengue
            ("aryan", "paracetamol", "500mg 3x/day (after meals)", TODAY),
            # Suresh — Diabetes + CKD + Hypertension
            ("suresh", "metformin", "500mg 2x/day (morning & night)", "2018-05-01"),
            ("suresh", "insulin_glargine", "20 units at bedtime", "2022-11-15"),
            ("suresh", "amlodipine", "5mg 1x/day (morning)", "2019-02-01"),
            ("suresh", "losartan", "50mg 1x/day (night)", "2022-11-15"),
            # Lakshmi — Asthma + Gastritis
            ("lakshmi", "salbutamol", "2 puffs as needed (max 4x/day)", "2020-06-01"),
            ("lakshmi", "omeprazole", "20mg 1x/day (before breakfast)", "2024-01-20"),
            # Dev — Typhoid
            ("dev", "azithromycin", "500mg 1x/day (morning)", TODAY),
            ("dev", "paracetamol", "500mg 3x/day (after meals, for fever)", TODAY),
            ("dev", "omeprazole", "20mg 1x/day (before breakfast)", TODAY),
            # Fatima — Rheumatoid Arthritis + Migraine
            ("fatima", "methotrexate", "15mg 1x/week (every Saturday)", "2023-07-01"),
            ("fatima", "hydroxychloroquine", "200mg 2x/day (morning & night)", "2023-07-01"),
            ("fatima", "diclofenac", "50mg 2x/day (after meals, for flare-ups)", "2023-07-01"),
            ("fatima", "paracetamol", "500mg as needed (for migraine)", "2022-01-15"),
        ]
        for pid, did, dosage, start in patient_meds:
            session.run(
                "MATCH (p:Patient {patient_id: $pid}), (d:Drug {drug_id: $did}) "
                "MERGE (p)-[r:TAKES_MEDICATION]->(d) SET r.dosage = $dosage, r.start_date = $start",
                pid=pid, did=did, dosage=dosage, start=start,
            )
        print(f"  -> {len(patient_meds)} patient-medication edges")

        # ─── PATIENT → LAB TESTS COMPLETED ───
        print("[Seed] Creating patient-labtest edges...")
        patient_tests = [
            # Priya
            ("priya", "lt_cbc", "2024-03-10", "low platelet count: 90,000/μL"),
            ("priya", "lt_fbs", "2024-01-05", "140 mg/dL (elevated)"),
            ("priya", "lt_hba1c", "2024-01-05", "6.8% (pre-diabetic range)"),
            # Karthik
            ("karthik", "lt_ecg", "2024-02-20", "normal sinus rhythm post-op"),
            ("karthik", "lt_echo", "2024-02-20", "EF 55%, mild LVH"),
            ("karthik", "lt_lipid", "2024-02-20", "LDL 145, HDL 38, Triglycerides 190"),
            # Ananya
            ("ananya", "lt_cbc", "2024-03-01", "Hb 9.2 g/dL (low), WBC 3,800/μL"),
            ("ananya", "lt_rf", "2024-03-01", "Negative"),
            # Rahul
            ("rahul", "lt_ecg", "2023-09-01", "ST depression in V4-V6"),
            ("rahul", "lt_lipid", "2023-09-01", "LDL 180, HDL 35"),
            ("rahul", "lt_hba1c", "2024-01-10", "7.2% (needs improvement)"),
            ("rahul", "lt_creatinine", "2024-01-10", "1.1 mg/dL (normal)"),
            # Meera
            ("meera", "lt_thyroid", "2023-03-10", "TSH 8.5 mIU/L (elevated), T4 low"),
            ("meera", "lt_cbc", "2023-09-15", "Hb 10.1 g/dL (mild anemia)"),
            # Aryan
            ("aryan", "lt_cbc", TODAY, "Platelet count: 85,000/μL (low), WBC: 3,200/μL (low)"),
            # Suresh
            ("suresh", "lt_hba1c", "2024-02-01", "8.1% (poorly controlled)"),
            ("suresh", "lt_creatinine", "2024-02-01", "2.8 mg/dL (elevated — Stage 3 CKD)"),
            ("suresh", "lt_fbs", "2024-02-01", "185 mg/dL (high)"),
            ("suresh", "lt_ecg", "2024-02-01", "LVH pattern"),
            # Lakshmi
            ("lakshmi", "lt_xray", "2024-01-20", "Hyperinflated lungs, no consolidation"),
            # Dev
            ("dev", "lt_cbc", TODAY, "WBC 12,500/μL (elevated), Hb 13.2 g/dL"),
            # Fatima
            ("fatima", "lt_rf", "2023-07-01", "Positive (68 IU/mL)"),
            ("fatima", "lt_cbc", "2023-07-01", "ESR 42 mm/hr (elevated)"),
            ("fatima", "lt_lft", "2024-01-15", "ALT 35, AST 30 (normal — monitoring for methotrexate)"),
        ]
        for pid, tid, test_date, result_val in patient_tests:
            session.run(
                "MATCH (p:Patient {patient_id: $pid}), (l:LabTest {lab_test_id: $tid}) "
                "MERGE (p)-[r:HAS_COMPLETED_TEST]->(l) SET r.test_date = $td, r.result = $res",
                pid=pid, tid=tid, td=test_date, res=result_val,
            )
        print(f"  -> {len(patient_tests)} patient-labtest edges")

        # ─── PATIENT → SYMPTOM (PRESENTS_WITH) ───
        print("[Seed] Creating patient-symptom edges...")
        patient_symptoms = [
            # Aryan — Dengue
            ("aryan", "fever"), ("aryan", "headache"), ("aryan", "body_aches"),
            ("aryan", "nausea"), ("aryan", "fatigue"), ("aryan", "chills"),
            ("aryan", "joint_pain"), ("aryan", "loss_of_appetite"),
            # Priya — Dengue + Diabetes
            ("priya", "fever"), ("priya", "headache"), ("priya", "fatigue"),
            ("priya", "body_aches"), ("priya", "rash"), ("priya", "frequent_urination"),
            # Ananya — Lupus + Anemia
            ("ananya", "rash"), ("ananya", "joint_pain"), ("ananya", "fatigue"),
            ("ananya", "hair_loss"), ("ananya", "fever"), ("ananya", "muscle_weakness"),
            ("ananya", "dizziness"),
            # Meera — Hypothyroid + Depression + Anemia
            ("meera", "fatigue"), ("meera", "weight_gain"), ("meera", "hair_loss"),
            ("meera", "depression_symptom"), ("meera", "insomnia"), ("meera", "dry_mouth"),
            ("meera", "loss_of_appetite"), ("meera", "dizziness"),
            # Suresh — Diabetes + CKD + Hypertension
            ("suresh", "fatigue"), ("suresh", "swelling_legs"), ("suresh", "frequent_urination"),
            ("suresh", "nausea"), ("suresh", "loss_of_appetite"), ("suresh", "muscle_weakness"),
            ("suresh", "blurred_vision"), ("suresh", "numbness"),
            # Lakshmi — Asthma + Gastritis
            ("lakshmi", "wheezing"), ("lakshmi", "shortness_of_breath"), ("lakshmi", "cough"),
            ("lakshmi", "abdominal_pain"), ("lakshmi", "nausea"), ("lakshmi", "loss_of_appetite"),
            # Dev — Typhoid
            ("dev", "fever"), ("dev", "headache"), ("dev", "abdominal_pain"),
            ("dev", "diarrhea"), ("dev", "loss_of_appetite"), ("dev", "fatigue"),
            # Fatima — RA + Migraine
            ("fatima", "joint_pain"), ("fatima", "fatigue"), ("fatima", "muscle_weakness"),
            ("fatima", "headache"), ("fatima", "nausea"), ("fatima", "blurred_vision"),
        ]
        for pid, sid in patient_symptoms:
            session.run(
                "MATCH (p:Patient {patient_id: $pid}), (s:Symptom {symptom_id: $sid}) "
                "MERGE (p)-[:PRESENTS_WITH]->(s)",
                pid=pid, sid=sid,
            )
        print(f"  -> {len(patient_symptoms)} patient-symptom edges")

        # ─── FOLLOW-UPS ───
        print("[Seed] Creating follow-ups...")
        followups = [
            ("fu_aryan_today", "pending", TODAY, "aryan", "Dengue Fever"),
            ("fu_karthik_today", "pending", TODAY, "karthik", "Coronary Artery Disease"),
            ("fu_priya_today", "pending", TODAY, "priya", "Dengue Fever"),
            ("fu_ananya_today", "pending", TODAY, "ananya", "Systemic Lupus Erythematosus"),
            ("fu_meera_today", "pending", TODAY, "meera", "Hypothyroidism"),
            ("fu_rahul_today", "pending", TODAY, "rahul", "Type 2 Diabetes"),
            ("fu_suresh_today", "pending", TODAY, "suresh", "Chronic Kidney Disease"),
            ("fu_lakshmi_today", "pending", TODAY, "lakshmi", "Asthma"),
            ("fu_dev_today", "pending", TODAY, "dev", "Typhoid Fever"),
            ("fu_fatima_today", "pending", TODAY, "fatima", "Rheumatoid Arthritis"),
        ]
        for fid, status, sched_date, pid, linked_disease in followups:
            session.run(
                "MERGE (fu:FollowUp {followup_id: $fid}) "
                "SET fu.status = $status, fu.scheduled_date = $sched, "
                "fu.pain_score = 0, fu.took_medication = false, fu.new_symptoms = '', "
                "fu.call_transcript = '', fu.risk_flag = false",
                fid=fid, status=status, sched=sched_date,
            )
            session.run(
                "MATCH (p:Patient {patient_id: $pid}), (fu:FollowUp {followup_id: $fid}) "
                "MERGE (p)-[r:HAS_FOLLOWUP]->(fu) SET r.linked_disease = $ld",
                pid=pid, fid=fid, ld=linked_disease,
            )
        print(f"  -> {len(followups)} follow-ups (due today)")

        # ─── DRUG SIDE EFFECT EDGES ───
        print("[Seed] Creating drug-side-effect edges...")
        side_effects = [
            ("metformin", "nausea", "common"), ("metformin", "diarrhea", "common"),
            ("warfarin", "bruising", "common"), ("warfarin", "bleeding_gums", "uncommon"),
            ("prednisolone", "weight_gain", "common"), ("prednisolone", "insomnia", "uncommon"),
            ("fluoxetine", "nausea", "common"), ("fluoxetine", "insomnia", "common"),
            ("amlodipine", "swelling_legs", "common"), ("amlodipine", "dizziness", "uncommon"),
            ("simvastatin", "muscle_weakness", "uncommon"),
        ]
        for did, sid, freq in side_effects:
            session.run(
                "MATCH (d:Drug {drug_id: $did}), (s:Symptom {symptom_id: $sid}) "
                "MERGE (d)-[r:CAUSES_SIDE_EFFECT]->(s) SET r.frequency = $freq",
                did=did, sid=sid, freq=freq,
            )
        print(f"  -> {len(side_effects)} drug-side-effect edges")

    driver.close()

    # ─── SUMMARY ───
    print("\n" + "=" * 50)
    print("[Seed] COMPLETE! Summary:")
    print(f"  Symptoms:      {len(symptoms)}")
    print(f"  Diseases:      {len(diseases)}")
    print(f"  Drugs:         {len(drugs)}")
    print(f"  Specialists:   {len(specialists)}")
    print(f"  Treatments:    {len(treatments)}")
    print(f"  Risk Factors:  {len(risk_factors)}")
    print(f"  Lab Tests:     {len(lab_tests)}")
    print(f"  Protocols:     {len(protocols)}")
    print(f"  Patients:      {len(patients)}")
    print(f"  Follow-ups:    {len(followups)} (pending for today)")
    print(f"  Total edges:   {len(disease_symptoms) + len(interactions) + len(referrals) + len(disease_treatments) + len(prescriptions) + len(disease_risks) + len(elevations) + len(disease_tests) + len(disease_protocols) + len(patient_conditions) + len(patient_meds) + len(patient_tests) + len(followups) + len(side_effects)}+")
    print("=" * 50)


if __name__ == "__main__":
    main()
