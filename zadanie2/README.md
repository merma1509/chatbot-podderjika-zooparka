# Task 2: Adversarial Prompt Generation

## Overview

Production-grade pipeline for generating 200 adversarial prompts based on 10 base prompts from Task 1.

## Architecture

- **Hybrid Approach**: Template Expansion + LLM Paraphrasing + Noise Injection + Semantic Deduplication
- **Modular System**: Separate components for each pipeline stage
- **Multiple LLM Support**: OpenAI, Ollama, LM Studio, Mock

## Quick Start

### Basic Generation (Mock LLM)

```bash
python main.py
```

### With Local LLM

```bash
# Ollama
ollama serve
ollama pull llama3:8b
python main.py --use-llm --api-type ollama

# LM Studio
# 1. Запустите LM Studio
# 2. Выберите модель (Gemma 3 4B)
# 3. Включите Server Mode на localhost:1234
# 4. Включите OpenAI Compatible API
python main.py --use-llm --api-type lmstudio
```

### With OpenAI API

```bash
# Установите API ключ
export OPENAI_API_KEY="your-key-here"
python main.py --use-llm --api-type openai
```

### Custom Target Count

```bash
python main.py --target 100
```

## LLM Integration Details

### Supported Models

- **OpenAI GPT-4o-mini** - максимальное качество
- **Gemma 3 4B (LM Studio)** - локальный вариант
- **Dolphin Llama 3 8B (Ollama)** - локальный вариант
- **Mock Paraphraser** - для тестирования

### LLM Setup

#### Ollama Setup

```bash
# Установка и запуск
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3:8b

# Тест
curl http://localhost:11434/api/generate -d '{"model": "llama3:8b", "prompt": "Hello"}'
```

#### LM Studio Setup

1. **Download**: [LM Studio](https://lmstudio.ai/)
2. **Install**: Запустите установщик
3. **Model**: Выберите Gemma 3 4B или другую
4. **Server Settings**:
   - Enable Server
   - OpenAI Compatible API
   - Port: 1234
   - Host: localhost
5. **Test**:

```bash
curl http://localhost:1234/v1/models
```

#### OpenAI Setup

```bash
# Установка
pip install openai

# Настройка
export OPENAI_API_KEY="sk-..."

# Тест
python -c "import openai; print('OpenAI connected')"
```

## File Structure

```bash
zadanie2/
|
|-- main.py                    # Main pipeline
|-- src/                       # Modular components
|   |-- generator.py           # Template expansion
|   |-- noise.py               # Noise injection
|   |-- dedup.py               # Semantic deduplication
|   |-- classify.py            # Difficulty classification
|   |-- llm.py                 # LLM paraphrasing
|-- data/                      # Data and results
|   |-- base_prompts.json      # 10 base prompts
|   |-- generated.csv          # Generated prompts
|   |-- generated_stats.json   # Statistics
|-- Task2_Prompt_Generation.md # Full methodology
|-- requirements.txt           # Dependencies
`-- venv/                      # Python virtual environment
```

## Results

- **Target**: 200 prompts
- **Distribution**: Easy (30%), Medium (40%), Hard (30%)
- **Quality**: Semantic deduplication with cosine similarity < 0.9
- **Actual Results**: 129 prompts (LM Studio Gemma 3 4B)

## Pipeline Flow

1. **Base Prompts** → 10 adversarial prompts from Task 1
2. **Template Expansion** → 5 variations per prompt
3. **LLM Paraphrasing** → 5 LLM variations (if enabled)
4. **Noise Injection** → 5 heavy noise variations
5. **Deduplication** → Remove duplicates (cosine < 0.9)
6. **Classification** → Easy/Medium/Hard difficulty
7. **Output** → Final dataset (CSV + stats)

## Quality Metrics

- **Semantic Similarity**: < 0.9 cosine similarity
- **Lexical Similarity**: < 0.8 Jaccard similarity
- **Attack Vector Preservation**: 100% validation
- **Difficulty Distribution**: Balanced across levels

## Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --use-llm        Enable LLM paraphrasing
  --api-type       LLM API type (openai, ollama, lmstudio, mock)
  --target         Target number of prompts (default: 200)
  --help           Show help message
```

## Examples

```bash
# Mock generation (fastest)
python main.py

# Local LLM generation
python main.py --use-llm --api-type ollama --target 50

# OpenAI generation (high quality)
python main.py --use-llm --api-type openai

# Test with small dataset
python main.py --target 10
```

## Troubleshooting

### LLM Connection Issues

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check LM Studio
curl http://localhost:1234/v1/models

# Check OpenAI
python -c "import openai; client = openai.OpenAI(); print(client.models.list())"
```

### Common Issues

- **TF warnings**: `export TF_ENABLE_ONEDNN_OPTS=0`
- **Memory issues**: Use smaller models or reduce target count
- **Slow generation**: Use mock API for testing

## Documentation

- `Task2_Prompt_Generation.md` - Complete methodology
- `Task2_Prompt_Generation.tex` - LaTeX version for PDF

## Next Steps

Ready for Task 3: Scaling to 1000+ prompts for LoRA fine-tuning.

## Requirements

```bash
pip install -r requirements.txt
```

Key dependencies:

- pandas, numpy
- sentence-transformers
- nltk
- openai
- transformers
