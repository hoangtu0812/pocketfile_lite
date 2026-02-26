"""
Seed script: creates default admin account and sample data.
Run inside the container: python seed.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import APKFile, Project, User, UserRole, Version


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Admin user ──
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                email="admin@company.com",
                password_hash=hash_password("Admin@123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.flush()
            print(f"  ✓ Admin user created  (username=admin, password=Admin@123)")
        else:
            admin = existing
            print("  • Admin user already exists, skipping.")

        # ── Sample user ──
        if not db.query(User).filter(User.username == "developer").first():
            dev = User(
                username="developer",
                email="dev@company.com",
                password_hash=hash_password("Dev@12345"),
                role=UserRole.USER,
            )
            db.add(dev)
            print("  ✓ Developer user created (username=developer, password=Dev@12345)")

        # ── Sample project ──
        project = db.query(Project).filter(Project.name == "SampleApp").first()
        if not project:
            project = Project(name="SampleApp", description="Sample Android application")
            db.add(project)
            db.flush()
            print(f"  ✓ Project 'SampleApp' created")

            # ── Sample version ──
            version = Version(version_string="1.0.0", project_id=project.id)
            db.add(version)
            db.flush()
            print(f"  ✓ Version '1.0.0' created")
        else:
            print("  • Sample project already exists, skipping.")

        db.commit()
        print("\n✅ Seed completed successfully!")
        print("\nDefault credentials:")
        print("  Admin   → username: admin     | password: Admin@123")
        print("  User    → username: developer | password: Dev@12345")
        print(f"\nApp URL: http://localhost:8000")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
