#!/bin/bash

# Function to make a curl request with a given query
make_request() {
    local query="$1"
    local description="$2"
    local service_name="$3"
    
    echo "Generating service: $service_name"
    echo "----------------------------------------"
    
    curl -X POST http://localhost:5000/query \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"$query\", \"service_name\": \"$service_name\"}"
    
    echo -e "\n\nWaiting 10 seconds before next request...\n"
    sleep 10
}

# Air Quality Service
make_request \
"Create a service that provides real-time and historical air quality measurements including AQI, PM2.5, PM10, NO2, and O3 levels for different locations. The service must:
- Use POST endpoint /air_quality
- Accept location (List[str]) and timestamp (Optional[str]) parameters
- Return measurements with AQI, PM2.5, PM10, NO2, O3 values
- Load data from data/air_quality_data.json
- Match the exact structure of the original air_quality service" \
"Air Quality Service" \
"air_quality"

# Restaurant Finder Service
make_request \
"Create a service that recommends restaurants based on user preferences. The service must:
- Use POST endpoint /restaurant_finder
- Accept cuisine_type (List[str]), price_range (List[int]), dietary_restrictions (List[str]), group_size (int) parameters
- Return filtered restaurant recommendations
- Load data from data/restaurant_data.json
- Match the exact structure of the original restaurant_finder service" \
"Restaurant Finder Service" \
"restaurant_finder"

# Historical Info Service
make_request \
"Create a service that provides historical information about monuments and sites. The service must:
- Use POST endpoint /historical_info
- Accept site_name (List[str]) parameter
- Return historical details for requested sites
- Load data from data/historic_data.json
- Match the exact structure of the original historical_info service" \
"Historical Information Service" \
"historical_info"

# Exhibition Tracker Service
make_request \
"Create a service that tracks museum and art exhibitions. The service must:
- Use POST endpoint /exhibition_tracker
- Accept interested_audience (List[str]), location (List[str]), date_range (str), exhibition_type (List[str]) parameters
- Return filtered exhibition information
- Load data from data/exhibition_data.json
- Match the exact structure of the original exhibition_tracker service" \
"Exhibition Tracker Service" \
"exhibition_tracker"

# Crowd Monitor Service
make_request \
"Create a service that monitors crowd density at locations. The service must:
- Use POST endpoint /crowd_monitor
- Accept location (str) and timestamp (Optional[str]) parameters
- Return crowd count for closest timestamp
- Load data from data/crowd_quality_data.json
- Match the exact structure of the original crowd_monitor service" \
"Crowd Monitor Service" \
"crowd_monitor"

# Event Notifier Service
make_request \
"Create a service that provides information about city events. The service must:
- Use POST endpoint /event_notifier
- Accept event_type (List[str]) and duration (List[str]) parameters
- Return filtered event information
- Load data from data/event_notifier.json
- Match the exact structure of the original event_notifier service" \
"Event Notifier Service" \
"event_notifier"

# Ticket Purchase Service
make_request \
"Create a service that helps users find available tickets. The service must:
- Use POST endpoint /ticket_purchase
- Accept event_name (List[str]) and price_range (List[int]) parameters
- Return ticket availability and pricing
- Load data from data/event_ticket_prices.csv
- Match the exact structure of the original ticket_purchase service" \
"Ticket Purchase Service" \
"ticket_purchase"

# Travel Options Service
make_request \
"Create a service that provides travel options. The service must:
- Use POST endpoint /travel_options
- Accept destination (List[str]), available_time (int), preferred_mode (List[str]) parameters
- Return filtered travel options
- Load data from data/travel.txt
- Match the exact structure of the original travel_options service" \
"Travel Options Service" \
"travel_options"

# Water Quality Service
make_request \
"Create a service that monitors water quality metrics. The service must:
- Use POST endpoint /water_quality
- Accept location (List[str]) and timestamp (Optional[str]) parameters
- Return water quality measurements (pH, Dissolved_Oxygen, Conductivity, Turbidity, Temperature)
- Load data from data/water_quality_data.json
- Match the exact structure of the original water_quality service" \
"Water Quality Service" \
"water_quality"

echo "All services generated!"