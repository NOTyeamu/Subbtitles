@echo off
chcp 65001 >nul

setlocal enabledelayedexpansion

REM === Настройки ===
set "model=vosk-model-small-en-us-0.15"
set "script=main.py"

REM === Проверка модели ===
if not exist "%model%" (
    echo Model folder not found: %model%
    echo Download from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    pause
    exit /b
)

REM === Проверка скрипта ===
if not exist "%script%" (
    echo Python script not found: %script%
    pause
    exit /b
)

REM === Поиск видео и аудио ===
set i=0
for %%f in (*.mp4 *.mp3) do (
    set /a i+=1
    set "file[!i!]=%%f"
)

if %i%==0 (
    echo No MP4 or MP3 files found in this folder.
    pause
    exit /b
)

echo Found %i% media file(s):
for /l %%n in (1,1,%i%) do echo   %%n. !file[%%n]!

echo.
set /p choice=Enter number of file to transcribe: 

if "%choice%"=="" (
    echo No choice entered.
    pause
    exit /b
)

if %choice% GTR %i% (
    echo Invalid choice.
    pause
    exit /b
)

set "selected=!file[%choice%]!"
echo.
echo ▶ Processing: %selected%
echo ------------------------------------------

python "%script%" "%selected%" "%model%"

echo ------------------------------------------
echo ✅ Done!
pause
