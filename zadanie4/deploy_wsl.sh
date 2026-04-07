#!/bin/bash

echo "=== WSL Task 4 Deployment ==="

# Use Windows Python directly
PYTHON_CMD="/mnt/c/Users/aimem/AppData/Local/Programs/Python/Python311/python.exe"
PIP_CMD="/mnt/c/Users/aimem/AppData/Local/Programs/Python/Python311/Scripts/pip.exe"

echo "Using Windows Python: $PYTHON_CMD"
echo "Using Windows Pip: $PIP_CMD"

# Create dirs
mkdir -p data specialized_scenarios

# Copy dataset if exists
if [ -f "../zadanie3/data/lora_training_dataset.json" ]; then
    cp ../zadanie3/data/lora_training_dataset.json ./data/
    echo "Dataset copied"
fi

# Install dependencies with Windows pip
echo "Installing dependencies..."
$PIP_CMD install fastapi uvicorn pydantic requests

# Train LoRA adapter if dataset exists
if [ -f "../zadanie3/data/lora_training_dataset.json" ]; then
    echo "Training LoRA adapter..."
    $PYTHON_CMD lora_trainer.py --model-type local --model-path "C:/Users/aimem/.lmstudio/models/dolphinnlp/Llama-3-8B-Instruct-exl2-6bpw" --dataset ../zadanie3/data/lora_training_dataset.json --output ./lora_adapter
    echo "LoRA training completed"
else
    echo "No dataset found, skipping LoRA training"
fi

# Generate scenarios
echo "Generating scenarios..."
$PYTHON_CMD scenario_generator.py

# Start server
echo "Starting server..."
$PYTHON_CMD local_llm_server.py &
SERVER_PID=$!

echo "Server started (PID: $SERVER_PID)"
sleep 5

# Check if server is actually running
echo "Checking server health..."
$PYTHON_CMD -c "import requests; r=requests.get('http://0.0.0.0:8000/health', timeout=5); print('✅ Server is running' if r.status_code==200 else print('❌ Server failed to start')" 2>/dev/null

# Test scenarios
echo "Testing scenarios..."
$PYTHON_CMD lora_evaluator.py

echo ""
echo "=== Results ==="
cat evaluation_results.json

# Stop server
kill $SERVER_PID 2>/dev/null
echo "Done!"
