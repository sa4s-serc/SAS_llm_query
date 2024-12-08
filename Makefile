# Makefile for cleaning temporary data

.PHONY: clean clean-pyc clean-apps clean-services clean

# Clean Python cache files
clean-pyc:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Clean generated apps
clean-apps:
	rm -rf app/generated_apps/*

# Clean services configuration
clean-services:
	rm -f app/services.toml
	rm -f data/services_state.json

# Clean all temporary files
clean: clean-pyc clean-apps clean-services
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 