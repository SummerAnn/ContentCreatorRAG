#!/bin/bash

echo "🎨 Starting CreatorFlow AI Frontend..."
echo ""

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies (this may take a minute)..."
    npm install
fi

echo "✅ Starting frontend server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev

