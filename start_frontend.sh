#!/bin/bash

# Start Frontend Server
echo "Starting Flowlytics Frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting React development server on http://localhost:3000"
npm run dev

