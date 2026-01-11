#!/bin/bash
# FastAPI Project Initialization Script
# Usage: bash init-project.sh <project-name> [template]
# Templates: hello-world (default), production

set -e

PROJECT_NAME=${1:-"my-fastapi-app"}
TEMPLATE=${2:-"hello-world"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"

echo "Creating FastAPI project: $PROJECT_NAME"
echo "Template: $TEMPLATE"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Copy template files
if [ "$TEMPLATE" = "production" ]; then
    cp -r "$ASSETS_DIR/production/"* .
    echo "Production template copied."
else
    cp -r "$ASSETS_DIR/hello-world/"* .
    echo "Hello World template copied."
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate and install dependencies
echo "Installing dependencies..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Project '$PROJECT_NAME' created successfully!"
echo ""
echo "To get started:"
echo "  cd $PROJECT_NAME"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "  venv\\Scripts\\activate"
else
    echo "  source venv/bin/activate"
fi
if [ "$TEMPLATE" = "production" ]; then
    echo "  cp .env.example .env"
    echo "  fastapi dev app/main.py"
else
    echo "  fastapi dev main.py"
fi
echo ""
echo "API docs will be available at: http://127.0.0.1:8000/docs"
