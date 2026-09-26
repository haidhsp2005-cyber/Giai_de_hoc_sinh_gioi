@echo off
chcp 65001 > nul
echo ========================================================
echo   HUONG DAN DAY CODE LEN GITHUB DE DEPLOY LEN RENDER
echo ========================================================
echo.
echo 1. Hay vao trang: https://github.com/new
echo 2. Dat ten Repository (vi du: hsg-solver-ai), de Public hoac Private tuy y.
echo 3. KHONG tich chon "Add a README file" hay .gitignore.
echo 4. Nhan "Create repository".
echo 5. Copy duong link HTTPS cua repo (vi du: https://github.com/username/hsg-solver-ai.git).
echo.
set /p REPO_URL="Dan duong link repo GitHub cua ban vao day: "

if "%REPO_URL%"=="" (
    echo [Loi] Ban chua nhap link repo!
    pause
    exit /b
)

echo.
echo [*] Dang ket noi toi GitHub repo...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [*] Dang day ma nguon len GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [LOI] Khong the push len GitHub. 
    echo Hay dam bao ban da dang nhap GitHub tren may va nhap dung link.
) else (
    echo.
    echo ========================================================
    echo   THANH CONG! Ma nguon da duoc day len GitHub!
    echo ========================================================
    echo Tiep theo:
    echo 1. Vao https://dashboard.render.com/
    echo 2. Nhan New + -> Web Service -> Chon repo vua push.
    echo 3. Nhap cac bien moi truong GEMINI_API_KEY va Deploy!
)

pause
