@echo off
chcp 65001 > nul
echo ========================================================
echo   HSG SOLVER AI - GIAI DE THI HOC SINH GIOI TIN HOC
echo ========================================================
echo.

:: 1. Uu tien nap duong dan Miniconda vao PATH de CMD tim thay Python ngay lap tuc
if exist "C:\ProgramData\miniconda3\python.exe" (
    set "PATH=C:\ProgramData\miniconda3;C:\ProgramData\miniconda3\Scripts;%PATH%"
    set "PYTHON_EXE=C:\ProgramData\miniconda3\python.exe"
) else (
    if exist "%USERPROFILE%\miniconda3\python.exe" (
        set "PATH=%USERPROFILE%\miniconda3;%USERPROFILE%\miniconda3\Scripts;%PATH%"
        set "PYTHON_EXE=%USERPROFILE%\miniconda3\python.exe"
    ) else (
        set "PYTHON_EXE=python"
    )
)

echo [1/2] Kiem tra ket noi dich vu Ollama...
curl -s http://localhost:11434/api/tags > nul
if errorlevel 1 (
    echo [THONG BAO] Chua mo Ollama tren cong 11434.
    echo He thong van hoat dong tot bang Google Gemini qua file .env.
    echo.
) else (
    echo [OK] Ollama dang hoat dong!
    echo.
)

echo [2/2] Dang khoi dong Web Server tren http://127.0.0.1:8000 ...
echo Python: %PYTHON_EXE%
echo Nhan Ctrl+C de dung server.
echo.

start "" "http://127.0.0.1:8000"
"%PYTHON_EXE%" -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
