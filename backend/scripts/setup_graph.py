"""
AyuNet Graph Setup Script
Creates Neo4j constraints, indexes, and prepares the database.
Run: cd backend && python scripts/setup_graph.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def main():
    print("[Setup] Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        session.run("RETURN 1")
    print("[Setup] Connected!")

    # =============================
    # STEP 1: CREATE CONSTRAINTS
    # =============================
    print("\n[Step 1] Creating uniqueness constraints...")

    constraints = [
        ("Patient", "patient_id"),
        ("Symptom", "symptom_id"),
        ("Disease", "disease_id"),
        ("Drug", "drug_id"),
        ("Specialist", "specialist_id"),
        ("Treatment", "treatment_id"),
        ("RiskFactor", "risk_factor_id"),
        ("LabTest", "lab_test_id"),
        ("Protocol", "protocol_id"),
        ("FollowUp", "followup_id"),
    ]

    with driver.session() as session:
        for label, prop in constraints:
            try:
                session.run(
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
                )
                print(f"  [OK] {label}.{prop} unique constraint")
            except Exception as e:
                print(f"  [SKIP] {label}.{prop}: {e}")

    # =============================
    # STEP 2: CREATE INDEXES
    # =============================
    print("\n[Step 2] Creating indexes for lookup performance...")

    indexes = [
        ("Patient", "name"),
        ("Symptom", "name"),
        ("Disease", "name"),
        ("Disease", "prevalence"),
        ("Drug", "name"),
        ("Specialist", "name"),
        ("Treatment", "name"),
        ("RiskFactor", "name"),
        ("LabTest", "name"),
        ("FollowUp", "status"),
        ("FollowUp", "scheduled_date"),
    ]

    with driver.session() as session:
        for label, prop in indexes:
            try:
                idx_name = f"idx_{label.lower()}_{prop}"
                session.run(
                    f"CREATE INDEX {idx_name} IF NOT EXISTS FOR (n:{label}) ON (n.{prop})"
                )
                print(f"  [OK] Index on {label}.{prop}")
            except Exception as e:
                print(f"  [SKIP] {label}.{prop}: {e}")

    # =============================
    # STEP 3: VERIFY
    # =============================
    print("\n[Step 3] Verifying setup...")
    with driver.session() as session:
        result = session.run("SHOW CONSTRAINTS")
        constraint_count = len(list(result))
        result = session.run("SHOW INDEXES")
        index_count = len(list(result))
        print(f"  Constraints: {constraint_count}")
        print(f"  Indexes: {index_count}")

    driver.close()

    print("\n" + "=" * 50)
    print("[Setup] DONE! Neo4j schema ready.")
    print("  - 10 uniqueness constraints")
    print("  - 11 lookup indexes")
    print("Next: run 'python scripts/seed_data.py' to populate data.")
    print("=" * 50)


if __name__ == "__main__":
    main()
