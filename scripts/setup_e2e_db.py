#!/usr/bin/env python
"""Setup database for E2E tests."""

import os
import sqlite3
import subprocess
from pathlib import Path


def main():
    """Setup E2E test database."""
    # Project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Set Django settings for E2E
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "django_project.totonoe_template.settings.e2e"
    )

    print("Setting up E2E test database...")

    # Ensure we have a clean DB for E2E tests
    e2e_db_path = project_root / "db_e2e.sqlite3"

    # Check if DB exists and has required tables
    db_needs_setup = False

    if not e2e_db_path.exists():
        print("Database file doesn't exist, creating new one...")
        db_needs_setup = True
    else:
        # Check if critical tables exist
        try:
            conn = sqlite3.connect(e2e_db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='wagtailcore_site'"
            )
            if not cursor.fetchone():
                print("wagtailcore_site table missing, recreating database...")
                db_needs_setup = True
            conn.close()
        except Exception as e:
            print(f"Error checking database: {e}")
            db_needs_setup = True

    if db_needs_setup:
        # Remove existing database
        if e2e_db_path.exists():
            e2e_db_path.unlink()

        # Run migrations
        print("Running migrations...")
        subprocess.run(
            ["uv", "run", "python", "manage.py", "migrate", "--run-syncdb"], check=True
        )

        # Create superuser if not exists
        print("Creating superuser...")
        try:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "manage.py",
                    "shell",
                    "-c",
                    "from django.contrib.auth import get_user_model; "
                    "User = get_user_model(); "
                    "User.objects.filter(username='admin').exists() or "
                    "User.objects.create_superuser('admin', 'admin@example.com', 'admin')",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            print("Superuser might already exist, continuing...")

        # Ensure Wagtail site exists
        print("Setting up Wagtail site...")
        try:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "manage.py",
                    "shell",
                    "-c",
                    (
                        "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.totonoe_template.settings.e2e'); "
                        "import django; django.setup(); "
                        "from wagtail.models import Site, Page; "
                        "print('Creating site...') if not Site.objects.exists() else print('Site exists'); "
                        "Site.objects.create(hostname='localhost', port=80, root_page=Page.objects.get(depth=1), is_default_site=True) if not Site.objects.exists() else None; "
                        "print(f'Site setup complete: {Site.objects.first()}')"
                    ),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Site setup failed: {e}, but continuing...")
            pass

        print("E2E database setup completed successfully!")
    else:
        print("Database already exists and appears to be properly configured.")

    # Verify the setup
    print("Verifying database setup...")
    conn = sqlite3.connect(e2e_db_path)
    cursor = conn.cursor()

    # Check critical tables
    tables_to_check = [
        "wagtailcore_site",
        "wagtailcore_page",
        "auth_user",
        "blog_blogpage",
    ]

    for table in tables_to_check:
        cursor.execute(f"SELECT count(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table {table}: {count} records")

    conn.close()
    print("Database verification completed!")


if __name__ == "__main__":
    main()
