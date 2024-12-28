import random
from typing import List, Dict


# def get_user_goal() -> str:
#     user_prompts = [
#         # Nature and Outdoor Spaces
#         "I want to visit Lumbini Park and see the light show.",
#         "Can you help me plan a picnic at Durgam Cheruvu Lake?",
#         "I'd like to go for a jog at KBR National Park.",
#         "I'm interested in hiking at Ananthagiri Hills.",
        
#         # Cuisine and Dining
#         "Where can I find the best Hyderabadi Biryani?",
#         "I want to explore the midnight food markets in Hyderabad.",
#         "Can you recommend a good place for Irani Chai?",
#         "I'd like to dine at a high-end restaurant with a view of the city.",
        
#         # Historical Monuments and Cultural Sites
#         "I want to visit Charminar and learn about its history.",
#         "Can you help me plan a tour of Golconda Fort?",
#         "I'd like to explore the Qutb Shahi Tombs.",
#         "I want to visit the Salar Jung Museum and see its famous exhibits.",
        
#         # Shopping and Local Markets
#         "I want to shop for bangles at Laad Bazaar.",
#         "Can you guide me to the best stores in GVK One Mall?",
#         # "Where can I find good souvenirs near Charminar?",
        
#         # Miscellaneous Events
#         "I want to attend the Bonalu Festival celebrations.",
#         "Can you tell me about any upcoming tech conferences in HITEC City?",
#         "I'd like to experience Diwali celebrations in Hyderabad.",
#         "Are there any local music concerts happening soon?"
#     ]
#     return random.choice(user_prompts)



# def get_user_goal() -> str:
#     user_prompts = [
#         # Historical Sites & Museums (mapping to historical_info, crowd_monitor, ticket_purchase)
#         "I'd love to visit Charminar and understand its history. Wonder if it gets too crowded on weekends?",
#         "The Golconda Fort sounds fascinating! I'd like to explore it thoroughly. What's the best way to get there?",
#         "I'm really interested in visiting Salar Jung Museum. Do they have any special exhibitions going on?",
#         "The Qutub Shahi Tombs look beautiful in photos. How can I plan a visit there?",
#         "I've heard Mecca Masjid is quite spectacular. What's the best time to visit?",

#         # Water Bodies & Parks (mapping to water_quality, air_quality)
#         "I'm thinking of spending some time near Hussain Sagar Lake. How clean is the water there?",
#         "Would love to visit Durgam Cheruvu for a peaceful evening. Is the area nice for walking?",
#         "I've heard Gandipet Lake is beautiful. How's the water quality there these days?",
#         "Thinking of having a peaceful morning at Mir Alam Tank. Is it good for a morning walk?",
#         "Would love to enjoy the sunset at Tank Bund. Is it usually very crowded in the evenings?",

#         # Shopping & Markets (mapping to crowd_monitor, travel_options)
#         "I want to explore Laad Bazaar for traditional bangles. What's the best way to reach there?",
#         "Planning to visit GVK One for some shopping. Is it usually very crowded on weekdays?",
#         "Would love to shop at Inorbit Mall. What's the easiest way to get there from the city center?",

#         # Food & Dining (mapping to restaurant_finder)
#         "Craving some authentic Hyderabadi biryani! Any vegetarian-friendly places you'd recommend?",
#         "Looking for a good place serving traditional Irani chai and Osmania biscuits!",
#         "Would love to try some street food. Any areas famous for chaat and local snacks?",
#         "Need a nice restaurant serving both South Indian and North Indian cuisine. We're a mixed group!",
#         "Looking for some good Bengali food. Any restaurants you'd suggest?",

#         # Cultural Events & Exhibitions (mapping to exhibition_tracker, ticket_purchase)
#         "Are there any cultural exhibitions happening in the city? Particularly interested in traditional art.",
#         "Would love to see some local handicraft exhibitions. Anything interesting coming up?",
#         "Any photography exhibitions or galleries worth visiting this week?",
#         "Interested in scientific exhibitions or interactive museums. What options do I have?",
        
#         # Entertainment (mapping to ticket_purchase, crowd_monitor)
#         "Thinking of visiting Snow World. Is it usually very crowded?",
#         "Would love to catch a concert or music show. Any upcoming events?",
#         "Planning to visit Ramoji Film City. What's the best way to plan this trip?"
#     ]
#     return random.choice(user_prompts)

def get_user_goal() -> str:
    user_prompts = [
        # CONCRETE GOALS (18)
        # 1. Services: [historical_info(site_name: golconda fort), crowd_monitor(location_name: golconda fort), 
        #              ticket_purchase(ticket_type: monument), travel_options(preferred_mode: [private_transport, auto_rickshaw, cab])]
        "The Golconda Fort sounds fascinating! I'd like to explore it thoroughly. What's the best way to get there?",
        
        # 2. Services: [historical_info(site_name: charminar), crowd_monitor(location_name: charminar)]
        "I'd love to visit Charminar and understand its history. Wonder if it gets too crowded on weekends?",
        
        # 3. Services: [historical_info(site_name: salar jung museum), 
        #              exhibition_tracker(exhibition_type: [art, historical, cultural]),
        #              ticket_purchase(ticket_type: museum)]
        "I'm really interested in visiting Salar Jung Museum. Do they have any special exhibitions going on?",
        
        # 4. Services: [historical_info(site_name: qutub shahi tombs), 
        #              travel_options(preferred_mode: [auto_rickshaw, cab])]
        "The Qutub Shahi Tombs look beautiful in photos. How can I plan a visit there?",
        
        # 5. Services: [water_quality(water_body_name: hussain sagar), 
        #              air_quality(locations: hyderabad)]
        "I'm thinking of spending some time near Hussain Sagar Lake. How clean is the water there?",
        
        # 6. Services: [water_quality(water_body_name: hussain sagar), 
        #              crowd_monitor(location_name: tank bund)]
        "Would love to enjoy the sunset at Tank Bund. Is it usually very crowded in the evenings?",
        
        # 7. Services: [water_quality(water_body_name: durgam cheruvu), 
        #              air_quality(locations: hitec city)]
        "Would love to visit Durgam Cheruvu for a peaceful evening. Is the area nice for walking?",
        
        # 8. Services: [crowd_monitor(location_name: laad bazaar), 
        #              travel_options(preferred_mode: [auto_rickshaw, cab])]
        "I want to explore Laad Bazaar for traditional bangles. What's the best way to reach there?",
        
        # 9. Services: [crowd_monitor(location_name: gvk one), 
        #              travel_options(preferred_mode: [metro, cab])]
        "Planning to visit GVK One for some shopping. Is it usually very crowded on weekdays?",
        
        # 10. Services: [restaurant_finder(cuisine_type: hyderabadi, dietary_restrictions: vegetarian)]
        "Craving some authentic Hyderabadi biryani! Any vegetarian-friendly places you'd recommend?",
        
        # 11. Services: [restaurant_finder(cuisine_type: street food, dietary_restrictions: vegetarian), 
        #               crowd_monitor(location_name: [charminar, laad bazaar])]
        "Would love to try some street food. Any areas famous for chaat and local snacks?",
        
        # 12. Services: [exhibition_tracker(exhibition_type: [art, cultural, traditional]), 
        #               ticket_purchase(ticket_type: museum)]
        "Are there any cultural exhibitions happening in the city? Particularly interested in traditional art.",
        
        # 13. Services: [exhibition_tracker(exhibition_type: [handicrafts, traditional]), 
        #               ticket_purchase(ticket_type: museum)]
        "Would love to see some local handicraft exhibitions. Anything interesting coming up?",
        
        # 14. Services: [ticket_purchase(ticket_type: theme_park)]
        "Thinking of visiting Snow World. Is it usually very crowded?",
        
        # 15. Services: [ticket_purchase(ticket_type: ramoji film city), 
        #               travel_options(preferred_mode: [private_transport, cab])]
        "Planning to visit Ramoji Film City. What's the best way to plan this trip?",
        
        # 16. Services: [restaurant_finder(cuisine_type: irani, dietary_restrictions: vegetarian)]
        "Looking for a good place serving traditional Irani chai and Osmania biscuits!",
        
        # 17. Services: [exhibition_tracker(exhibition_type: [photography, art])]
        "Any photography exhibitions or galleries worth visiting this week?",
        
        # 18. Services: [water_quality(water_body_name: gandipet lake), 
        #               air_quality(locations: hyderabad)]
        "I've heard Gandipet Lake is beautiful. How's the water quality there these days?",

        # AMBIGUOUS GOALS (7)
        # 19. Services: [historical_info(site_name: [charminar, mecca masjid]), 
        #               crowd_monitor(location_name: [charminar, laad bazaar]),
        #               restaurant_finder(cuisine_type: [hyderabadi, irani], dietary_restrictions: [vegetarian, non_veg])]
        "My grandparents always talk about Hyderabad's old charm. Want to experience that authentic vibe and maybe try some traditional snacks.",
        
        # 20. Services: [historical_info(site_name: [charminar, golconda fort]), 
        #               restaurant_finder(cuisine_type: [hyderabadi, mughlai], dietary_restrictions: non_veg)]
        "Been reading about Hyderabad's royal history. Would love to see some of that grandeur and taste what the Nizams enjoyed!",
        
        # 21. Services: [water_quality(water_body_name: hussain sagar), 
        #               restaurant_finder(cuisine_type: [continental, north indian], dietary_restrictions: [vegetarian, non_veg])]
        "I keep seeing these gorgeous lake photos on Instagram. Would love to spend an evening there and grab dinner nearby!",
        
        # 22. Services: [crowd_monitor(location_name: [laad bazaar, charminar]),
        #               restaurant_finder(cuisine_type: street food, dietary_restrictions: vegetarian),
        #               travel_options(preferred_mode: auto_rickshaw)]
        "Love those bustling market vibes, you know? Where locals shop and grab quick bites. That's my scene!",
        
        # 23. Services: [exhibition_tracker(exhibition_type: [art, cultural]), 
        #               historical_info(site_name: salar jung museum),
        #               restaurant_finder(cuisine_type: hyderabadi)]
        "Love anything artsy with a story behind it. Places where I can learn about local culture while enjoying the atmosphere.",
        
        # 24. Services: [historical_info(site_name: [charminar, golconda fort]), 
        #               restaurant_finder(cuisine_type: [hyderabadi, street food], dietary_restrictions: [vegetarian, non_veg]),
        #               exhibition_tracker(exhibition_type: historical)]
        "History nerd but also a foodie. Want to explore places that tell a story while munching on local specialties!",
        
        # 25. Services: [restaurant_finder(cuisine_type: [hyderabadi, street food]), 
        #               crowd_monitor(location_name: [charminar, laad bazaar]),
        #               travel_options(preferred_mode: [auto_rickshaw, private_transport])]
        "First time in Hyderabad! Want to start with the locals' favorites, not the tourist checklist."
    ]
    return random.choice(user_prompts)

# Load microservices
def load_microservices(file_path: str) -> List[Dict[str, str]]:
    microservices = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                try:
                    name, description = line.strip().split(",", 1)
                    microservices.append({"name": name.strip(), "description": description.strip()})
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    print(microservices)                    
    return microservices

# load_microservices("microservices.txt")
def load_summary(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            summary = f.read().strip()
        return summary
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except IOError:
        print(f"Error: Unable to read file at {file_path}")
        return ""
    
# print(load_summary("summary.txt"))

def load_service_parameters(file_path: str) -> dict:
    """
    Loads service parameters from a file and returns a nested dictionary structure.
    
    Args:
        file_path (str): Path to the parameters file
        
    Returns:
        dict: Nested dictionary of service parameters
        Format:
        {
            'service_name': {
                'param_name': list_of_values
            }
        }
    """
    service_params = {}
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                    
                # Split the line into service.param=values
                service_param, values = line.split('=')
                service_name, param_name = service_param.split('.')
                
                # Initialize service dictionary if it doesn't exist
                if service_name not in service_params:
                    service_params[service_name] = {}
                
                # Convert comma-separated values to list
                value_list = [v.strip() for v in values.split(',')]
                
                # Store parameters
                service_params[service_name][param_name] = value_list
                
        return service_params
        
    except FileNotFoundError:
        print(f"Error: Parameter file not found at {file_path}")
        return {}
    except Exception as e:
        print(f"Error loading parameters: {str(e)}")
        return {}


# print(load_service_parameters("service_params.txt"))

def write_output(results: dict, output_file: str) -> None:
    """
    Write simulation results to a file with timing information.
    
    Args:
        results (dict): Dictionary containing simulation results and metadata
        output_file (str): Path to the output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write simulation metadata
        f.write(f"Simulation Index: {results['simulation_index']}\n")
        f.write(f"Time taken: {results['simulation_time']:.2f} seconds\n")
        f.write(f"User Goal: {results.get('user_goal', 'Not specified')}\n")
        f.write(f"Available Hours: {results.get('available_hours', 'Not specified')}\n")
        f.write("----------------------------------------\n\n")

        # Write conversation with service tracking
        f.write("Conversation with Service Tracking:\n")
        for turn, entry in enumerate(results.get('conversation', []), 1):
            role = entry.get('role', 'Unknown')
            content = entry.get('content', 'No content')
            f.write(f"\n{role}:\n{content}\n")

            # If there are identified services after this turn
            services = entry.get('identified_services', [])
            if services:
                f.write(f"\nIdentified Services after Turn {turn}:\n")
                f.write(", ".join(services) + "\n")

        # Write final summary if available
        if 'final_summary' in results:
            f.write("\nFinal Plan Summary:\n")
            f.write(results['final_summary'] + "\n")

        # Write service parameters if available
        if 'service_parameters' in results:
            f.write("\nCore Services and Parameters:\n")
            f.write(results['service_parameters'] + "\n")

        # Write any error information if present
        if 'error' in results:
            f.write("\nError Information:\n")
            f.write(results['error'] + "\n")