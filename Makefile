.PHONY: help install install-dev test lint format clean deploy export-requirements

# Default ComfyUI path - can be overridden with: make deploy COMFYUI_PATH=/path/to/ComfyUI
COMFYUI_PATH ?= $(HOME)/ComfyUI

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## Install pre-commit hooks and sync all dependencies using uv
	@uv run pre-commit install
	@uv sync --locked --all-groups

install: ## Install dependencies using uv
	@uv sync --locked

install-dev: ## Install development dependencies using uv
	@uv sync --locked --all-groups

export-requirements: ## Export dependencies to requirements.txt for pip compatibility
	command uv export --no-cache --no-dev --locked > requirements.txt
	@echo "Dependencies exported to requirements.txt"

test: ## Run tests
	@uv run pytest -vvv .

test-coverage: ## Run tests with coverage report
	@uv run pytest -v --cov=src --cov-report=html --cov-report=term

format: # Format the code using isort, autoflake, and black
	@uv run isort .
	@uv run autoflake .
	@uv run black .

lint: #Check code formatting and linting without modifying files
	@uv run isort . --check-only
	@uv run flake8 .
	@uv run black . --check

clean: ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Define the ComfyUI path, default if not set
COMFYUI_PATH ?= $(HOME)/Documents/ComfyUI
# Define the path to ComfyUI's pip executable
COMFYUI_PIP = $(COMFYUI_PATH)/.venv/bin/pip

deploy: ## Deploy to local ComfyUI custom_nodes folder
	@echo "Deploying AdForge to ComfyUI custom_nodes..."

	# Check if the ComfyUI directory actually exists
	@if [ ! -d "$(COMFYUI_PATH)" ]; then \
		echo "Error: ComfyUI not found at $(COMFYUI_PATH)"; \
		echo "Set COMFYUI_PATH environment variable or use: make deploy COMFYUI_PATH=/path/to/ComfyUI"; \
		exit 1; \
	fi

	# Create the directory
	@mkdir -p $(COMFYUI_PATH)/custom_nodes/comfyui_adforge

	# Copy the files
	@echo "Copying files to $(COMFYUI_PATH)/custom_nodes/comfyui_adforge..."
	@cp -r __init__.py src tests pyproject.toml README.md LICENSE $(COMFYUI_PATH)/custom_nodes/comfyui_adforge/

	@echo "Deployment complete! Restart ComfyUI to load the extension. You may need to install dependencies in the ComfyUI environment."

deploy-link: ## Create symlink in ComfyUI custom_nodes folder (for development)
	@echo "Creating symlink in ComfyUI custom_nodes..."
	@if [ ! -d "$(COMFYUI_PATH)" ]; then \
		echo "Error: ComfyUI not found at $(COMFYUI_PATH)"; \
		echo "Set COMFYUI_PATH environment variable or use: make deploy-link COMFYUI_PATH=/path/to/ComfyUI"; \
		exit 1; \
	fi
	@mkdir -p $(COMFYUI_PATH)/custom_nodes
	@ln -sf $(PWD) $(COMFYUI_PATH)/custom_nodes/comfyui_adforge
	@echo "Symlink created! Restart ComfyUI to load the extension."
	@echo "Note: You'll need t o install dependencies manually in the ComfyUI environment"

undeploy: ## Remove from ComfyUI custom_nodes folder
	@echo "Removing AdForge from ComfyUI custom_nodes..."
	@if [ -L "$(COMFYUI_PATH)/custom_nodes/comfyui_adforge" ]; then \
		rm $(COMFYUI_PATH)/custom_nodes/comfyui_adforge; \
		echo "Symlink removed."; \
	elif [ -d "$(COMFYUI_PATH)/custom_nodes/comfyui_adforge" ]; then \
		rm -rf $(COMFYUI_PATH)/custom_nodes/comfyui_adforge; \
		echo "Directory removed."; \
	else \
		echo "AdForge not found in $(COMFYUI_PATH)/custom_nodes/"; \
	fi

setup-env:
	@echo "Creating .env file from .env.example..."
	@cp -n .env.example src/adforge_nodes/.env || true
	@echo ".env file created at src/adforge_nodes/.env. Please open it and fill in your credentials."
