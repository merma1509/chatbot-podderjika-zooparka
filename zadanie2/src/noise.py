#!/usr/bin/env python3
"""Noise Injection Module
Инъекция шума и искажений текста"""

import random
import string

def add_typos(text, probability=0.1):
    """
    Добавляет опечатки в текст
    
    Args:
        text: исходный текст
        probability: вероятность опечатки на символ
    
    Returns:
        str: текст с опечатками
    """
    result = []
    for char in text:
        if random.random() < probability:
            # Пропуск буквы (30%)
            if random.random() < 0.3:
                continue
            # Замена на похожую букву (70%)
            elif char.isalpha():
                # Замена на соседнюю букву клавиатуры
                replacements = {
                    'о': ['о', 'а', 'п'], 'а': ['а', 'о', 'с'],
                    'е': ['е', 'и', 'н'], 'и': ['и', 'е', 'п'],
                    'н': ['н', 'г', 'к'], 'с': ['с', 'в', 'а']
                }
                if char.lower() in replacements:
                    result.append(random.choice(replacements[char.lower()]))
                else:
                    result.append(char)
            else:
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)

def add_spacing(text):
    """
    Добавляет лишние пробелы между буквами
    
    Args:
        text: исходный текст
    
    Returns:
        str: текст с лишними пробелами
    """
    words = text.split()
    result_words = []
    
    for word in words:
        if random.random() < 0.3:  # 30% шанс
            # Разделяем слово пробелами
            spaced_word = ' '.join(list(word))
            result_words.append(spaced_word)
        else:
            result_words.append(word)
    
    return ' '.join(result_words)

def add_unicode_distortion(text):
    """
    Добавляет unicode искажения
    
    Args:
        text: исходный текст
    
    Returns:
        str: текст с unicode искажениями
    """
    # Замена кириллицы на похожие символы
    replacements = {
        'а': ['а', 'a'], 'о': ['о', 'o', '0'],
        'е': ['е', 'e', '3'], 'и': ['и', 'u', 'n'],
        'л': ['л', 'l', '1'], 'к': ['к', 'k']
    }
    
    result = text.lower()
    for original, chars in replacements.items():
        if random.random() < 0.4:  # 40% шанс замены
            result = result.replace(original, random.choice(chars))
    
    return result

def mixed_noise(text):
    """
    Применяет случайный тип шума
    
    Args:
        text: исходный текст
    
    Returns:
        str: текст с шумом
    """
    noise_funcs = [add_typos, add_spacing, add_unicode_distortion]
    return random.choice(noise_funcs)(text)

def heavy_noise(text):
    """
    Тяжелые искажения для Hard уровня
    
    Args:
        text: исходный текст
    
    Returns:
        str: сильно искаженный текст
    """
    # Комбинация нескольких методов
    result = add_typos(text, probability=0.2)
    result = add_unicode_distortion(result)
    
    # Добавляем случайные пробелы
    if random.random() < 0.5:
        result = ' '.join(list(result))
    
    return result

if __name__ == "__main__":
    # Тест
    test_text = "Сколько стоят билеты на панд?"
    print(f"Оригинал: {test_text}")
    print(f"Опечатки: {add_typos(test_text)}")
    print(f"Пробелы: {add_spacing(test_text)}")
    print(f"Unicode: {add_unicode_distortion(test_text)}")
    print(f"Смешанный: {mixed_noise(test_text)}")
    print(f"Тяжелый: {heavy_noise(test_text)}")
