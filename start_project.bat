@echo off
:: GradeOps Dev Launcher
:: Starts all 4 services: FastAPI, OCR Worker, Grading Worker, Frontend
:: 
:: SETUP: Set your conda environment name below (default: base)
:: Find yours by running: conda env list

set CONDA_ENV=base

:: Auto-detect project root (the folder containing this .bat file)
set PROJECT_ROOT=%~dp0
set BACKEND=%PROJECT_ROOT%backend
set FRONTEND=%PROJECT_ROOT%frontend

echo Starting GradeOps development environment...
echo Project root: %PROJECT_ROOT%
echo Conda env:    %CONDA_ENV%
echo.

start "GradeOps - FastAPI" cmd /k "conda activate %CONDA_ENV% && cd /d %BACKEND% && uvicorn main:app --reload"
timeout /t 2 /nobreak >nul

start "GradeOps - OCR Worker" cmd /k "conda activate %CONDA_ENV% && cd /d %BACKEND% && celery -A worker.celery_app worker -Q ocr -c 1 --pool=solo --loglevel=info"
timeout /t 1 /nobreak >nul

start "GradeOps - Grading Worker" cmd /k "conda activate %CONDA_ENV% && cd /d %BACKEND% && celery -A worker.celery_app worker -Q grading -c 1 --pool=solo --loglevel=info"
timeout /t 1 /nobreak >nul

start "GradeOps - Frontend" cmd /k "cd /d %FRONTEND% && npm run dev"

echo.
echo All 4 services launched. Open http://localhost:5173