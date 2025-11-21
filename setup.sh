#!/bin/bash

echo "🚀 Setting up CreatorFlow AI..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/uploads data/projects

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Build and start containers
echo "🐳 Building Docker containers..."
docker-compose build || docker compose build

echo "🚀 Starting services..."
docker-compose up -d || docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Pull default Ollama model
echo "🤖 Downloading default language model (this may take a few minutes)..."
docker exec creatorflow-ollama ollama pull llama3.1:8b-instruct || echo "⚠️  Could not pull model. You may need to do this manually: ollama pull llama3.1:8b-instruct"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000/docs"
echo "🤖 Ollama: http://localhost:11434"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""

