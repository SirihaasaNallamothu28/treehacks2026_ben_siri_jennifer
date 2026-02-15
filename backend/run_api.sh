#!/bin/bash
# Simple script to run the FastAPI backend

echo "Starting Synapsis API server..."
echo "API will be available at http://localhost:8009"
echo ""

# Make sure we're in the backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the API
python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8009
