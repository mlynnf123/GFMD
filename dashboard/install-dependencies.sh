#!/bin/bash

echo "🚀 Installing GFMD Dashboard Dependencies..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Install dependencies
echo "📦 Installing npm dependencies..."
npm install

# Install additional UI dependencies if not in package.json
echo "🎨 Installing Shadcn UI components..."
npx shadcn-ui@latest add button card tabs dialog dropdown-menu

# Install additional chart dependencies
echo "📊 Installing chart dependencies..."
npm install recharts date-fns

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "⚙️ Creating .env.local from example..."
    cp .env.local.example .env.local
    echo "✏️ Please edit .env.local with your Firebase configuration"
fi

echo "✅ Installation complete!"
echo ""
echo "🔥 Next steps:"
echo "1. Edit .env.local with your Firebase configuration"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 See README.md for detailed setup instructions"