@echo off

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Install Poetry
pip install poetry

REM Install project dependencies
poetry install

REM Install dotenv
pip install python-dotenv

REM Initialize the database
poetry run python -c "from db import init_db; init_db()"

echo Installation complete. You can now run the application using:
echo poetry run python app.py