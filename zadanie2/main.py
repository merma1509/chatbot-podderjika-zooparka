#!/usr/bin/env python3
"""
Main Pipeline for Adversarial Prompt Generation
Задание 2: Генерация 200 запросов на основе 10 базовых
"""

import json
import pandas as pd
import random
import os
from pathlib import Path

# Импорт модулей
from src import apply_templates, mixed_noise, heavy_noise, quick_deduplicate, DifficultyClassifier, create_paraphraser

# Конфигурация
TOTAL_PER_PROMPT = 20
TARGET_COUNT = 200
SEED = 42

random.seed(SEED)

class PromptGenerator:
    def __init__(self, use_llm=False, api_type="mock"):
        """
        Инициализация генератора
        
        Args:
            use_llm: использовать LLM для перефразирования
            api_type: тип API ("openai", "local", "mock")
        """
        self.use_llm = use_llm
        self.paraphraser = create_paraphraser(api_type) if use_llm else None
        self.classifier = DifficultyClassifier()
        
        # Загрузка базовых промптов
        with open("data/base_prompts.json", "r", encoding="utf-8") as f:
            self.base_prompts = json.load(f)
    
    def generate_variations(self, base_prompt):
        """
        Генерирует вариации для одного базового промпта
        
        Args:
            base_prompt: dict с полями id, text, attack_type
        
        Returns:
            list: список вариаций
        """
        variations = []
        
        # 1. Template expansion (5 вариаций)
        template_vars = apply_templates(base_prompt["text"], n=5)
        variations.extend(template_vars)
        
        # 2. LLM paraphrasing (5 вариаций) - если включен
        if self.use_llm and self.paraphraser:
            try:
                llm_vars = self.paraphraser.paraphrase(base_prompt["text"], n=5)
                variations.extend(llm_vars)
                print(f"✓ LLM перефразирован: {base_prompt['text'][:50]}...")
            except Exception as e:
                print(f"✗ Ошибка LLM: {e}")
                # Fallback на template expansion
                fallback_vars = apply_templates(base_prompt["text"], n=5)
                variations.extend(fallback_vars)
        
        # 3. Noise injection (5 вариаций)
        noise_vars = []
        for _ in range(5):
            noise_var = mixed_noise(base_prompt["text"])
            noise_vars.append(noise_var)
        variations.extend(noise_vars)
        
        # 4. Combined variations (5 вариаций)
        combined_vars = []
        for _ in range(5):
            # Сначала template, потом noise
            template_var = apply_templates(base_prompt["text"], n=1)[0]
            combined_var = heavy_noise(template_var)
            combined_vars.append(combined_var)
        variations.extend(combined_vars)
        
        return variations
    
    def classify_variations(self, variations, base_prompt):
        """
        Классифицирует вариации по сложности
        
        Args:
            variations: список вариаций
            base_prompt: базовый промпт
        
        Returns:
            list: список словарей с классификацией
        """
        classified = []
        
        for var in variations:
            difficulty = self.classifier.classify(var)
            
            # Определение метода генерации
            method = "paraphrase"
            if self.use_llm and var in variations[:5]:  # Первые 5 могут быть LLM
                method = "llm_paraphrase"
            elif any(char.isdigit() for char in var) or " " in " ".join(list(var)):
                method = "heavy_noise"
            elif var != base_prompt["text"]:
                method = "paraphrase+light_noise"
            
            classified.append({
                "prompt": var,
                "difficulty": difficulty,
                "generation_method": method
            })
        
        return classified
    
    def generate_dataset(self):
        """
        Генерирует полный датасет
        
        Returns:
            pd.DataFrame: датафрейм с результатами
        """
        all_rows = []
        
        print("🚀 Генерация adversarial промптов...")
        print(f"📊 Целевое количество: {TARGET_COUNT}")
        print(f"📊 Использование LLM: {self.use_llm}")
        
        for i, base_prompt in enumerate(self.base_prompts, 1):
            print(f"\n📝 Обработка промпта {i}/{len(self.base_prompts)}: {base_prompt['attack_type']}")
            
            # Генерация вариаций
            variations = self.generate_variations(base_prompt)
            
            # Дедупликация
            unique_variations = quick_deduplicate(variations)
            
            # Классификация
            classified = self.classify_variations(unique_variations, base_prompt)
            
            # Ограничение количества
            for var_data in classified[:TOTAL_PER_PROMPT]:
                all_rows.append({
                    "id": len(all_rows) + 1,
                    "base_id": base_prompt["id"],
                    "prompt": var_data["prompt"],
                    "attack_type": base_prompt["attack_type"],
                    "difficulty": var_data["difficulty"],
                    "generation_method": var_data["generation_method"]
                })
            
            print(f"✓ Сгенерировано {len(classified[:TOTAL_PER_PROMPT])} вариаций")
        
        # Обрезка до целевого количества
        df = pd.DataFrame(all_rows[:TARGET_COUNT])
        
        return df
    
    def save_results(self, df, output_file="data/generated.csv"):
        """
        Сохраняет результаты
        
        Args:
            df: датафрейм с результатами
            output_file: путь к выходному файлу
        """
        # Создание директории
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Сохранение CSV
        df.to_csv(output_file, index=False, encoding="utf-8")
        
        # Генерация статистики
        stats = self.generate_stats(df)
        
        # Сохранение статистики
        stats_file = output_file.replace('.csv', '_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Генерация завершена!")
        print(f"📊 Всего сгенерировано: {len(df)} промптов")
        print(f"💾 Результаты сохранены:")
        print(f"   - {output_file}")
        print(f"   - {stats_file}")
        
        return stats
    
    def generate_stats(self, df):
        """
        Генерирует статистику по датасету
        
        Args:
            df: датафрейм с промптами
        
        Returns:
            dict: статистика
        """
        stats = {
            "total_prompts": len(df),
            "attack_types": df["attack_type"].value_counts().to_dict(),
            "difficulty_levels": df["difficulty"].value_counts().to_dict(),
            "generation_methods": df["generation_method"].value_counts().to_dict()
        }
        
        print("\n📈 Распределение по типам атак:")
        for attack_type, count in stats["attack_types"].items():
            print(f"   {attack_type}: {count}")
        
        print("\n📈 Распределение по сложности:")
        for difficulty, count in stats["difficulty_levels"].items():
            print(f"   {difficulty}: {count}")
        
        print("\n📈 Распределение по методам генерации:")
        for method, count in stats["generation_methods"].items():
            print(f"   {method}: {count}")
        
        return stats

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Генерация adversarial промптов")
    parser.add_argument("--use-llm", action="store_true", 
                      help="Использовать LLM для перефразирования")
    parser.add_argument("--api-type", choices=["openai", "local", "mock"], 
                      default="mock", help="Тип API для LLM")
    parser.add_argument("--target", type=int, default=TARGET_COUNT,
                      help=f"Целевое количество промптов (по умолчанию {TARGET_COUNT})")
    
    args = parser.parse_args()
    
    # Создание генератора
    generator = PromptGenerator(use_llm=args.use_llm, api_type=args.api_type)
    
    # Генерация датасета
    df = generator.generate_dataset()
    
    # Сохранение результатов
    stats = generator.save_results(df)
    
    # Показ первых примеров
    print("\n🎯 Первые 10 примеров:")
    for i, row in df.head(10).iterrows():
        print(f"{i+1}. [{row['attack_type']}] {row['prompt']}")

if __name__ == "__main__":
    main()
