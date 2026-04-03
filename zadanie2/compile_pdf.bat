@echo off
REM Скрипт для компиляции LaTeX в PDF (Windows)

echo Компиляция LaTeX документа...

REM Проверка наличия pdflatex
where pdflatex >nul 2>nul
if %errorlevel% neq 0 (
    echo Ошибка: pdflatex не найден. Установите MiKTeX или TeX Live
    pause
    exit /b 1
)

REM Компиляция (дважды для корректной нумерации ссылок)
pdflatex Task2_Prompt_Generation.tex
pdflatex Task2_Prompt_Generation.tex

REM Очистка временных файлов
del /q *.aux *.log *.toc *.out *.fdb_latexmk *.fls *.synctex.gz 2>nul

echo Компиляция завершена! Файл Task2_Prompt_Generation.pdf создан.
pause
