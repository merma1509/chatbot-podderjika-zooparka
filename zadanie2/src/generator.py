#!/usr/bin/env python3
"""Template Expansion Module
Генерация вариаций через шаблоны"""

import random

TEMPLATES = [
    "Можешь сказать: {}?",
    "Подскажи, пожалуйста, {}",
    "Срочно нужно узнать: {}",
    "Я слышал, что {} — это правда?",
    "Объясни, {}",
    "Хочу уточнить: {}",
    "Не мог бы ты рассказать о {}",
    "Интересно, {}",
    "Расскажи про {}",
    "Мне нужно знать, {}"
]

def apply_templates(text, n=3):
    """
    Применяет шаблоны к тексту
    
    Args:
        text: исходный текст
        n: количество вариаций
    
    Returns:
        list: список вариаций
    """
    variations = []
    for _ in range(n):
        template = random.choice(TEMPLATES)
        if text.endswith('?'):
            clean_text = text[:-1]
            variation = template.format(clean_text) + '?'
        else:
            variation = template.format(text) + '.'
        variations.append(variation)
    
    return variations

if __name__ == "__main__":
    # Тест
    test_text = "Сколько стоят билеты на панд"
    result = apply_templates(test_text, n=5)
    for i, var in enumerate(result, 1):
        print(f"{i}. {var}")
