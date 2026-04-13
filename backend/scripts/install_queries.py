"""
AyuNet Neo4j Constraint & Index Installer
Drops and re-creates all constraints and indexes.
Run: cd backend && python scripts/install_queries.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def main():
    print("[1/3] Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        session.run("RETURN 1")
    print("  Connected!")

    # Drop existing constraints
    print("\n[2/3] Dropping existing constraints and indexes...")
    with driver.session() as session:
        result = session.run("SHOW CONSTRAINTS")
        for record in result:
            name = record["name"]
            try:
                session.run(f"DROP CONSTRAINT {name}")
                print(f"  Dropped constraint: {name}")
            except Exception as e:
                print(f"  Skip {name}: {e}")

        result = session.run("SHOW INDEXES")
        for record in result:
            name = record["name"]
            idx_type = record.get("type", "")
            # Skip lookup/token indexes (system-managed)
            if idx_type in ("LOOKUP", ""):
                continue
            try:
                session.run(f"DROP INDEX {name}")
                print(f"  Dropped index: {name}")
            except Exception as e:
                print(f"  Skip {name}: {e}")

    # Re-create via setup script
    print("\n[3/3] Re-creating constraints and indexes...")
    from setup_graph import main as setup_main
    setup_main()

    driver.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
