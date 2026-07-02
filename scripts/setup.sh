#!/usr/bin/env bash
set -euo pipefail

echo "=== Insight Brasil - Setup ==="

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r backend/requirements/base.txt
pip install -r backend/requirements/development.txt

cp -n .env.example .env 2>/dev/null || true

python backend/manage.py migrate

echo "Setup concluído!"
echo ""
echo "Para rodar o backend:  python backend/manage.py runserver"
echo "Para rodar o frontend: streamlit run frontend/app.py"
