# AWS Flask Blog HA Lab

Minimal text-only Flask blog backed by PostgreSQL. Shows the responding EC2 instance ID and AZ for ALB demonstrations.

## Local setup

1. `docker compose up -d`
2. `python -m venv .venv` and activate the virtual environment
3. `pip install -r requirements.txt`
4. `cp .env.example .env` (PowerShell: `Copy-Item .env.example .env`)
5. `python run.py`
6. Open http://127.0.0.1:8000

Check `/health` and `/instance-info`.

## AWS notes

- Set `DATABASE_URL` to the RDS connection string and `RUNNING_ON_EC2=true`.
- Run `gunicorn --bind 0.0.0.0:8000 run:app` on Linux EC2.
- Restrict port 8000 to the ALB security group, and PostgreSQL 5432 to the application security group.
- Use Secrets Manager/SSM for DB secrets, not Git or user data.
- Require IMDSv2 on the EC2 Launch Template.
- This is a demo without authentication, CSRF protection, or production-grade migrations. Do not expose the create-post endpoint publicly in a real production application.
