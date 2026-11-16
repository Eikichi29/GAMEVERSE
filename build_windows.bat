\
    @echo off
    setlocal EnableExtensions
    cd /d "%~dp0"
    title GAMESVERSE - Build Windows

    echo ==========================================
    echo       GAMESVERSE 0.5.0 - WINDOWS BUILD
    echo ==========================================
    echo.

    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PY=py -3.12"
    ) else (
        set "PY=python"
    )

    %PY% --version
    if errorlevel 1 goto :error

    %PY% -m pip install --upgrade pip
    if errorlevel 1 goto :error
    %PY% -m pip install -r requirements.txt pyinstaller
    if errorlevel 1 goto :error

    where ISCC.exe >nul 2>nul
    if errorlevel 1 (
        echo Inno Setup 6 is required.
        echo Install it from https://jrsoftware.org/isinfo.php
        echo Then run this file again.
        pause
        exit /b 1
    )

    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist installer-output rmdir /s /q installer-output

    %PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
      --name GAMESVERSE --collect-all PySide6 ^
      --add-data "assets;assets" --add-data "catalogue.json;." main.py
    if errorlevel 1 goto :error

    ISCC.exe GAMESVERSE.iss
    if errorlevel 1 goto :error

    echo.
    echo BUILD COMPLETE:
    echo   dist\GAMESVERSE.exe
    echo   installer-output\GAMESVERSE-Setup-0.5.0.exe
    echo.
    pause
    exit /b 0

    :error
    echo.
    echo BUILD FAILED. Read the error above.
    pause
    exit /b 1
