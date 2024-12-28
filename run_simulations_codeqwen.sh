#!/bin/bash

# Create the output directory if it doesn't exist
mkdir -p runs/codeqwen
source /home/bassam/Documents/research/code/goal_parser/venv/bin/activate
# Run 100 simulations
for i in {1..100}
do
    echo "Running simulation $i of 100..."
    
    # Run the simulation
    python simulate_codeqwen.py "runs/codeqwen/$i.txt"
    
    # Check if the simulation was successful
    if [ $? -eq 0 ]; then
        echo "Simulation $i completed successfully"
    else
        echo "Simulation $i failed"
    fi
    
    # Sleep for 5 seconds before next simulation
    if [ $i -lt 100 ]; then
        echo "Waiting for 5 seconds before next simulation..."
        sleep 5
    fi
    
    # Print a separator for better readability
    echo "----------------------------------------"
done

echo "All simulations completed!"