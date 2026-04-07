#!/bin/bash

echo "=== Simple Task 4 Deployment ==="

# Create dirs
mkdir -p data specialized_scenarios

# Copy dataset if exists
if [ -f "../zadanie3/data/lora_training_dataset.json" ]; then
    cp ../zadanie3/data/lora_training_dataset.json ./data/
    echo "Dataset copied"
fi

# Generate scenarios
echo "Generating scenarios..."
python3 scenario_generator.py

# Start server
echo "Starting server..."
python3 local_llm_server.py &
SERVER_PID=$!

echo "Server started (PID: $SERVER_PID)"
sleep 5

# Check if server is actually running
echo "Checking server health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Server is running"
else
    echo "Server failed to start"
    exit 1
fi

# Test scenarios
echo "Testing scenarios..."
python3 lora_evaluator.py

echo ""
echo "=== Results ==="
cat evaluation_results.json

# Stop server
kill $SERVER_PID 2>/dev/null
echo "Done!"
