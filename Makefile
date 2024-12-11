# Makefile for cleaning temporary data and generating services

.PHONY: clean clean-pyc clean-apps clean-services clean air_quality restaurant_finder historical_info exhibition_tracker crowd_monitor event_notifier ticket_purchase travel_options water_quality

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
	
clean-cupcarbon:
	rm -rf app/cupcarbon/results/*

# Clean all temporary files
clean: clean-pyc clean-apps clean-cupcarbon
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 

# Service generation targets
air:
	@echo "Generating air_quality service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that provides real-time and historical air quality measurements. The service must: 1) Use POST endpoint /air_quality, 2) Accept location (Optional[List[str]]) and timestamp (Optional[str]) parameters, 3) Return measurements with AQI, PM2.5, PM10, NO2, O3 values in a dict with measurements and message keys, 4) Load data from data/air_quality_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "air_quality"}'

restaurant:
	@echo "Generating restaurant_finder service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that recommends restaurants. The service must: 1) Use POST endpoint /restaurant_finder, 2) Accept cuisine_type (Optional[List[str]]), price_range (Optional[List[int]]), dietary_restrictions (Optional[List[str]]), group_size (Optional[int]) parameters, 3) Return filtered restaurants in a dict with results and message keys, 4) Load data from data/restaurant_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "restaurant_finder"}'

history:
	@echo "Generating historical_info service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that provides historical information. The service must: 1) Use POST endpoint /historical_info, 2) Accept site_name (Optional[List[str]]) parameter, 3) Return historical details in a dict with sites and message keys, 4) Load data from data/historic_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "historical_info"}'

exhibition:
	@echo "Generating exhibition_tracker service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that tracks exhibitions. The service must: 1) Use POST endpoint /exhibition_tracker, 2) Accept interested_audience (Optional[List[str]]), location (Optional[List[str]]), date_range (Optional[str]), exhibition_type (Optional[List[str]]) parameters, 3) Return exhibitions in a dict with exhibitions and message keys, 4) Load data from data/exhibition_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "exhibition_tracker"}'

crowd:
	@echo "Generating crowd_monitor service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that monitors crowd density. The service must: 1) Use POST endpoint /crowd_monitor, 2) Accept location (str) and timestamp (Optional[str]) parameters, 3) Return crowd data in a dict with measurements and message keys, 4) Load data from data/crowd_quality_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "crowd_monitor"}'

event:
	@echo "Generating event_notifier service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that provides event information. The service must: 1) Use POST endpoint /event_notifier, 2) Accept event_type (Optional[List[str]]) and duration (Optional[List[str]]) parameters, 3) Return events in a dict with events and message keys, 4) Load data from data/event_notifier.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "event_notifier"}'

ticket:
	@echo "Generating ticket_purchase service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that handles ticket purchases. The service must: 1) Use POST endpoint /ticket_purchase, 2) Accept event_name (Optional[List[str]]) and price_range (Optional[List[int]]) parameters, 3) Return tickets in a dict with tickets and message keys, 4) Load data from data/event_ticket_prices.csv, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "ticket_purchase"}'

travel:
	@echo "Generating travel_options service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that provides travel options. The service must: 1) Use POST endpoint /travel_options, 2) Accept destination (Optional[List[str]]), available_time (Optional[int]), preferred_mode (Optional[List[str]]) parameters, 3) Return options in a dict with options and message keys, 4) Load data from data/travel.txt, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "travel_options"}'

water:
	@echo "Generating water_quality service..."
	@curl -s -X POST http://localhost:5000/query \
		-H "Content-Type: application/json" \
		-d '{"query": "Create a FastAPI service that monitors water quality. The service must: 1) Use POST endpoint /water_quality, 2) Accept location (Optional[List[str]]) and timestamp (Optional[str]) parameters, 3) Return measurements with pH, Dissolved_Oxygen, Conductivity, Turbidity, Temperature in a dict with measurements and message keys, 4) Load data from data/water_quality_data.json, 5) Use proper async/await and error handling, 6) Log all operations with self.logger", "service_name": "water_quality"}'

# Generate all services
generate: air_quality restaurant_finder historical_info exhibition_tracker crowd_monitor event_notifier ticket_purchase travel_options water_quality