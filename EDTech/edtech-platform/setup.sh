#!/bin/bash
# ============================================================
#  EduPlatform — One-Click Local Setup Script
#  Usage: bash setup.sh
# ============================================================

set -e  # Exit on any error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "======================================"
echo "  EduPlatform — Local Setup Starting  "
echo "======================================"
echo -e "${NC}"

# ── Step 1: Check Python ──
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
python3 --version || { echo -e "${RED}Python 3 not found. Install it first.${NC}"; exit 1; }

# ── Step 2: Create virtual environment ──
echo -e "${YELLOW}[2/8] Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo "  ✅ Virtual environment activated"

# ── Step 3: Upgrade pip & install dependencies ──
echo -e "${YELLOW}[3/8] Installing Python dependencies...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  ✅ Dependencies installed"

# ── Step 4: Copy .env file ──
echo -e "${YELLOW}[4/8] Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ✅ .env file created from .env.example"
    echo -e "  ${RED}⚠️  Edit .env and add your DB, Razorpay, AWS credentials!${NC}"
else
    echo "  ✅ .env file already exists"
fi

# ── Step 5: Create logs directory ──
echo -e "${YELLOW}[5/8] Creating required directories...${NC}"
mkdir -p logs staticfiles media
echo "  ✅ Directories created"

# ── Step 6: Run migrations ──
echo -e "${YELLOW}[6/8] Running database migrations...${NC}"
python manage.py makemigrations users courses payments videos live_classes notifications
python manage.py migrate
echo "  ✅ Migrations applied"

# ── Step 7: Collect static files ──
echo -e "${YELLOW}[7/8] Collecting static files...${NC}"
python manage.py collectstatic --noinput --quiet
echo "  ✅ Static files collected"

# ── Step 8: Create superuser ──
echo -e "${YELLOW}[8/8] Creating superuser...${NC}"
echo ""
python manage.py createsuperuser
echo "  ✅ Superuser created"

echo ""
echo -e "${GREEN}======================================"
echo "  ✅ Setup Complete!"
echo "======================================"
echo ""
echo "  Run the server:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Admin panel:"
echo "    http://127.0.0.1:8000/admin/"
echo ""
echo "  API base URL:"
echo "    http://127.0.0.1:8000/api/v1/"
echo ""
echo "  To run Celery worker (in separate terminal):"
echo "    celery -A config worker -l info"
echo ""
echo "  To run with Docker:"
echo "    docker-compose up --build"
echo -e "======================================${NC}"
