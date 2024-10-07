#!/bin/bash

output_file="microservice_info.txt"

> "$output_file"

extract_description() {
    grep -oP 'description="\K[^"]+' "$1"
}

for dir in app/microservices/*/; do
    service_name=$(basename "$dir")
    
    service_file="${dir}service.py"
    
    if [[ -f "$service_file" ]]; then
        description=$(extract_description "$service_file")
        
        if [[ ! -z "$description" ]]; then
            echo "$service_name, $description" >> "$output_file"
        else
            echo "$service_name: No description found" >> "$output_file"
        fi
    else
        echo "$service_name: No service.py file found" >> "$output_file"
    fi
done

echo "Microservice information has been saved to $output_file"