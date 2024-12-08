#!/bin/bash

# Function to make a curl request with a given query
make_request() {
    local query="$1"
    local description="$2"
    
    echo "Making request for: $description"
    echo "----------------------------------------"
    
    curl -X POST http://localhost:5000/query \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"$query\"}"
    
    echo -e "\n\nWaiting 20 seconds before next request...\n"
    sleep 20
}

# Air Quality
make_request "Create a service that provides real-time and historical air quality measurements including AQI, PM2.5, PM10, NO2, and O3 levels for different locations. It should accept location names and an optional timestamp to get the closest readings for those locations" "Air Quality Service"

# Restaurant Finder
make_request "Create a service that recommends restaurants based on user preferences including location, cuisine type, price range, dietary restrictions, and group size. The service should filter restaurants according to all these criteria and return matching options" "Restaurant Finder Service"

# Historical Info
make_request "Create a service that provides historical and cultural information about monuments and sites. The service should accept one or more site names and return comprehensive historical details including significance, year built, and cultural importance for each requested site" "Historical Information Service"

# Exhibition Tracker
make_request "Create a service that tracks museum and art exhibitions based on audience type (general, student, specialist), venue location, exhibition dates, and category (painting, sculpture, photography, etc). The service should handle multiple filter values and return matching exhibitions with details like venue, ticket prices, and featured artists" "Exhibition Tracker Service"

# Crowd Monitor
make_request "Create a service that monitors crowd density at different locations. It should accept a location and optional timestamp parameter, returning the crowd count for the closest matching timestamp" "Crowd Monitor Service"

# Event Notifier
make_request "Create a service that provides information about city events, festivals, and shows based on category (music, theater, sports, etc) and time commitment (1-hour, half-day, full-day, multi-day). It should handle multiple filter options and return matching events with details like timing, location, and booking information" "Event Notifier Service"

# Ticket Purchase
make_request "Create a service that helps users find available tickets based on event names and price ranges. It should handle multiple events and price ranges, returning ticket availability and pricing information" "Ticket Purchase Service"

# Travel Options
make_request "Create a service that provides travel options based on destination, available time, and preferred mode of transport. It should filter options based on these criteria and return matching travel possibilities" "Travel Options Service"

# Water Quality
make_request "Create a service that monitors water quality metrics in different locations. It should accept location names and an optional timestamp, returning pH, Dissolved Oxygen, Conductivity, Turbidity, and Temperature measurements for the closest matching timestamp" "Water Quality Service"

echo "All requests completed!"