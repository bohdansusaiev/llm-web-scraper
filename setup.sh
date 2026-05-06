#!/bin/bash
set -e

echo "=== Adaptive Web Scraper Setup ==="
echo ""

echo "[1/4] Creating virtual environment..."
python3 -m venv .venv

echo "[2/4] Activating virtual environment and upgrading pip..."
source .venv/bin/activate
pip install --upgrade pip -q

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt -q

echo "[4/4] Installing Playwright Chromium browser for Crawl4AI..."
python3 -m playwright install chromium --with-deps

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. cp .env.example .env"
echo "  2. Edit .env and add your DEEPSEEK_API_KEY"
echo "  3. Start the backend:      uvicorn main:app --reload"
echo "  4. In another terminal:    streamlit run ui.py"
echo ""
echo "Open your browser at http://localhost:8501"
