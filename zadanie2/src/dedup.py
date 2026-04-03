#!/usr/bin/env python3
"""
Semantic Deduplication Module
Удаление семантически похожих промптов
"""

from sentence_transformers import SentenceTransformer, util
import numpy as np

class SemanticDeduplicator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Инициализация модели для семантического сравнения
        
        Args:
            model_name: название модели sentence-transformers
        """
        self.model = SentenceTransformer(model_name)
    
    def encode_texts(self, texts):
        """
        Кодирует тексты в векторы
        
        Args:
            texts: список текстов
        
        Returns:
            np.array: матрица эмбеддингов
        """
        return self.model.encode(texts, convert_to_tensor=True)
    
    def cosine_similarity(self, emb1, emb2):
        """
        Вычисляет косинусное сходство
        
        Args:
            emb1, emb2: эмбеддинги
        
        Returns:
            float: косинусное сходство
        """
        return util.cos_sim(emb1, emb2)[0]
    
    def deduplicate(self, prompts, threshold=0.9):
        """
        Удаляет дубликаты на основе семантического сходства
        
        Args:
            prompts: список промптов
            threshold: порог сходства для удаления дубликатов
        
        Returns:
            list: список уникальных промптов
        """
        if not prompts:
            return []
        
        # Кодируем все промпты
        embeddings = self.encode_texts(prompts)
        unique = []
        unique_indices = []
        
        for i, current_emb in enumerate(embeddings):
            is_duplicate = False
            
            # Проверяем с уже добавленными уникальными
            for j, unique_idx in enumerate(unique_indices):
                unique_emb = embeddings[unique_idx]
                similarity = self.cosine_similarity(current_emb, unique_emb)
                
                if similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(prompts[i])
                unique_indices.append(i)
        
        return unique
    
    def jaccard_similarity(self, text1, text2):
        """
        Вычисляет Jaccard similarity для лексической дедупликации
        
        Args:
            text1, text2: тексты для сравнения
        
        Returns:
            float: Jaccard similarity
        """
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0
    
    def lexical_deduplicate(self, prompts, threshold=0.8):
        """
        Лексическая дедупликация на основе Jaccard similarity
        
        Args:
            prompts: список промптов
            threshold: порог сходства
        
        Returns:
            list: список уникальных промптов
        """
        unique = []
        
        for prompt in prompts:
            is_duplicate = False
            
            for existing in unique:
                similarity = self.jaccard_similarity(prompt, existing)
                if similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(prompt)
        
        return unique

# Простая функция для быстрой дедупликации
def quick_deduplicate(prompts, semantic_threshold=0.9, lexical_threshold=0.8):
    """
    Быстрая дедупликация с использованием обеих метрик
    
    Args:
        prompts: список промптов
        semantic_threshold: порог семантического сходства
        lexical_threshold: порог лексического сходства
    
    Returns:
        list: список уникальных промптов
    """
    # Сначала лексическая фильтрация (быстрее)
    deduplicator = SemanticDeduplicator()
    lexically_unique = deduplicator.lexical_deduplicate(prompts, lexical_threshold)
    
    # Затем семантическая (точнее)
    return deduplicator.deduplicate(lexically_unique, semantic_threshold)

if __name__ == "__main__":
    # Тест
    test_prompts = [
        "Сколько стоят билеты на панд?",
        "Какая цена билетов на панд?",
        "Стоимость билетов панды?",
        "Сколько нужно заплатить за панд?"
    ]
    
    print("Тест дедупликации:")
    unique = quick_deduplicate(test_prompts)
    print(f"Всего: {len(test_prompts)}")
    print(f"Уникальных: {len(unique)}")
    for i, prompt in enumerate(unique, 1):
        print(f"{i}. {prompt}")
