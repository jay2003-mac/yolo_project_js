@echo off
REM X-Ray Screw Detection - Quick Commands
REM Run from project directory: quickstart.bat [command]

setlocal enabledelayedexpansion

set "PYTHON=.venv\Scripts\python.exe"

if "%1%"=="" (
    echo.
    echo ======================================================
    echo   X-Ray Screw Detection - Quick Start
    echo ======================================================
    echo.
    echo AVAILABLE COMMANDS:
    echo.
    echo   quickstart generate      - Generate synthetic data
    echo   quickstart validate      - Validate dataset
    echo   quickstart train         - Train model (M3)
    echo   quickstart train-all     - Train all screw types
    echo   quickstart list          - List trained models
    echo   quickstart status        - Show project status
    echo   quickstart camera        - Show camera config
    echo.
    echo EXAMPLES:
    echo   quickstart train              # Train M3 model
    echo   quickstart train m4 50 16     # Train M4, 50 epochs, batch 16
    echo.
) else if "%1%"=="generate" (
    echo Generating synthetic dataset...
    %PYTHON% main.py generate
) else if "%1%"=="validate" (
    echo Validating dataset...
    %PYTHON% main.py validate --type m3
) else if "%1%"=="train" (
    set type=m3
    set epochs=20
    set batch=32
    if not "%2%"=="" set type=%2%
    if not "%3%"=="" set epochs=%3%
    if not "%4%"=="" set batch=%4%
    echo Training %type% model ^(epochs=%epochs%, batch=%batch%^)...
    %PYTHON% main.py train --type %type% --epochs %epochs% --batch %batch%
) else if "%1%"=="train-all" (
    set epochs=20
    if not "%2%"=="" set epochs=%2%
    echo Training all screw types ^(epochs=%epochs%^)...
    %PYTHON% main.py train-all --epochs %epochs%
) else if "%1%"=="list" (
    %PYTHON% main.py list
) else if "%1%"=="status" (
    %PYTHON% main.py status
) else if "%1%"=="camera" (
    %PYTHON% main.py camera
) else if "%1%"=="help" (
    %PYTHON% main.py help
) else (
    echo Unknown command: %1%
    echo Run 'quickstart' without arguments to see available commands
)

endlocal
