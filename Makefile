# ==============================================================================
# Makefile for E-Commerce Business Intelligence & Customer Analytics Platform
# ==============================================================================

.PHONY: run setup etl test report clean help

help:
	@echo "Available commands:"
	@echo "  make run      - Launch both Backend (FastAPI) and Frontend (React) in one command"
	@echo "  make setup    - Install all backend (pip) and frontend (npm) dependencies"
	@echo "  make etl      - Execute the end-to-end data ingestion, cleaning, and DB population"
	@echo "  make test     - Run automated test suite (Pytest)"
	@echo "  make report   - Generate executive PDF report and Excel export"
	@echo "  make clean    - Remove build artifacts, cache, and temporary files"

run:
	python run.py

setup:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install

etl:
	python backend/etl/etl_pipeline.py

test:
	python -m pytest tests/ -v

report:
	python backend/reports/report_generator.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/dist
