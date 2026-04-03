#!/bin/bash
# Скрипт для компиляции LaTeX в PDF

echo "Компиляция LaTeX документа..."

# Проверка наличия pdflatex
if ! command -v pdflatex &> /dev/null; then
    echo "Ошибка: pdflatex не найден. Установите TeX Live или MiKTeX"
    exit 1
fi

# Компиляция (дважды для корректной нумерации ссылок)
pdflatex Task2_Prompt_Generation.tex
pdflatex Task2_Prompt_Generation.tex

# Очистка временных файлов
rm -f *.aux *.log *.toc *.out *.fdb_latexmk *.fls *.synctex.gz

echo "Компиляция завершена! Файл Task2_Prompt_Generation.pdf создан."
