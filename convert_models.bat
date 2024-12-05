@echo off
python -m generator.src.test_model_converter
if %ERRORLEVEL% EQU 0 (
    python -m generator.src.model_converter ../../meta/m01/models.py
)
pause
