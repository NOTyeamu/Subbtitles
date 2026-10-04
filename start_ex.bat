@echo off
chcp 65001 >nul
set "model=vosk-model-small-ru-0.22"
set "script=ex.py"

echo Вставьте все ссылки в файл links.txt и сохраните его.
echo После этого нажмите любую клавишу.
pause >nul

if exist "links.txt" (
    echo ▶ Начинаю сборку из сегментов...
    python "%script%" "links.txt" "%model%"
) else (
    echo Файл links.txt не найден!
)
pause