#!/bin/bash

# Quick test script to verify frontend configuration

echo "🧪 Testing Frontend Configuration"
echo "================================="
echo ""

# Check if config.js exists
if [ -f "config.js" ]; then
    echo "✅ config.js exists"
    echo "   Content:"
    cat config.js | grep BACKEND_URL
else
    echo "❌ config.js not found"
    exit 1
fi

echo ""

# Check if index.html includes config.js
if grep -q "config.js" index.html; then
    echo "✅ index.html includes config.js"
else
    echo "❌ index.html doesn't include config.js"
    exit 1
fi

echo ""

# Check if app.js uses window.BACKEND_URL
if grep -q "window.BACKEND_URL" app.js; then
    echo "✅ app.js uses window.BACKEND_URL"
else
    echo "❌ app.js doesn't use window.BACKEND_URL"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "To test locally:"
echo "1. Make sure backend is running on port 8080"
echo "2. Run: python -m http.server 3000"
echo "3. Open: http://localhost:3000"
