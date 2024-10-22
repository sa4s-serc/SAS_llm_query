# Common Data
## Locations
- Lumbini Park
- Hussain Sagar Lake
- KBR National Park
- Durgam Cheruvu Lake
- Ananthagiri Hills
- Botanical Gardens
- Charminar
- Golconda Fort
- Mecca Masjid
- Chowmahalla Palace
- Qutb Shahi Tombs
- Salar Jung Museum
- Laad Bazaar
- HITEC City
- GVK One Mall

## Exhibition Types
- Home Decor Exhibition
- Fashion Show
- Cosmetics Expo
- Music Festival
- Textile Fair
- Craft Beer Festival
- Wellness Expo
- Antique Fair
- Handicrafts Fair
- Shoe Exhibition
- Gardening Show
- Vintage Collectibles Show

# Air Quality Data Format

## File: `air_quality_data.json`

## Structure
JSON array of objects, each representing an air quality measurement.

## Object Properties
- `location`: String (see Locations list)
- `timestamp`: String (format: "YYYY-MM-DDTHH:MM:SS", 5-minute intervals)
- `AQI`: Integer (50 to 150)
- `PM2.5`: Float (5 to 20, 1 decimal place)
- `PM10`: Float (10 to 35, 1 decimal place)
- `NO2`: Float (15 to 30, 1 decimal place)
- `O3`: Float (20 to 40, 1 decimal place)


## Data Volume
- 15 locations
- 1000 timestamps per location
- Total: 15,000 records

## Sample Data
```json
[
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:21:40",
        "AQI": 106,
        "PM2.5": 6.6,
        "PM10": 29.3,
        "NO2": 16.9,
        "O3": 39.9
    },
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:16:40",
        "AQI": 82,
        "PM2.5": 16.1,
        "PM10": 32.6,
        "NO2": 18.3,
        "O3": 29.5
    },
    {
        "location": "Qutb Shahi Tombs",
        "timestamp": "2024-10-20T03:06:40",
        "AQI": 97,
        "PM2.5": 10.1,
        "PM10": 35.0,
        "NO2": 26.9,
        "O3": 34.9
    }
]
```

# Crowd Quality Data Format

## File: `crowd_quality_data.json`

## Structure
JSON array of objects, each representing a crowd quality measurement.

## Object Properties
- `location`: String (see Locations list)
- `timestamp`: String (format: "YYYY-MM-DDTHH:MM:SS", 5-minute intervals)
- `crowd_count`: Integer (Poisson distribution with lambda=500, minimum 1)

## Data Volume
- 15 locations
- 1000 timestamps per location
- Total: 15,000 records

## Note
Crowd count is generated using a Poisson distribution with an average (lambda) of 500, ensuring a minimum value of 1.

## Sample Data
```json
[
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:45:42",
        "crowd_count": 533
    },
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:40:42",
        "crowd_count": 483
    },
    {
        "location": "Qutb Shahi Tombs",
        "timestamp": "2024-10-21T17:05:42",
        "crowd_count": 499
    }
]
```

# Event Notifier Data Format
## File: `event_notifier`

## Structure
List of strings, each representing an event.

## Sample Data
```
1. Hyderabad Cultural Dance Festival
Time Required: 2 hours
Details: A showcase of classical and folk dances from across India, featuring Kuchipudi, Bharatanatyam, and Kathak performances. The festival celebrates the rich cultural diversity of Hyderabad, bringing together renowned dancers and artists from across the country.
2. Lumbini Park Laser Light Show
Time Required: 45 minutes
Details: A spectacular laser light and fountain show at Lumbini Park, set against the backdrop of Hussain Sagar Lake. The show narrates the history of Hyderabad using vibrant lights, water jets, and music, creating a mesmerizing experience for visitors.
3. Golconda Fort Sound and Light Show
Time Required: 1 hour 30 minutes
Details: A dramatic sound and light show at the historic Golconda Fort that recounts the rise and fall of the Qutb Shahi dynasty. With the majestic fort as the backdrop, the show immerses audiences in the history of the Deccan region.
...
```

# Historic Data

## File: `historic_data`

## Structure
List of strings, each representing a historic site.

## Sample Data
```
Charminar:
The Charminar, located in the heart of Hyderabad, is one of India’s most iconic landmarks. Built in 1591 by Sultan Muhammad Quli Qutb Shah, the Charminar is a grand testament to the architectural brilliance of the Qutb Shahi dynasty. The monument was constructed to commemorate the founding of Hyderabad and to mark the end of a deadly plague that had ravaged the region.....

Golconda Fort:
Golconda Fort, a majestic fortress located on the outskirts of Hyderabad, is a monumental reminder of the grandeur of the Qutb Shahi dynasty. Originally a mud fort constructed by the Kakatiya dynasty in the 12th century, Golconda was later fortified by the Qutb Shahi rulers in the 16th century into the massive citadel that stands today....

...

```

# Restaurant Data Format

## File: `restaurant_data.json`

## Structure
JSON array of objects, each representing a restaurant.

## Object Properties
- `location`: String (see Locations list)
- `restaurant_name`: String (format: "[Cuisine] Place [1-100]")
- `cuisine_type`: String (see Cuisines list)
- `price_range(per person)`: Integer (see Price Ranges list)
- `dietary_restrictions`: String (see Dietary Restrictions list)
- `group_size`: Integer (see Group Sizes list)


## Cuisines
Indian, Chinese, Italian, Mexican, Continental, Thai, Fast Food, Vegetarian, Vegan

## Price Ranges
1000, 500, 2500, 750, 1300

## Dietary Restrictions
None, Vegetarian, Vegan, Gluten-Free, Nut-Free

## Group Sizes
1, 2, 4, 6, 8, 10

## Data Volume
- 15 locations
- 5 restaurants per location
- Total: 75 restaurant entries

## Sample Data
```json
[
    {
        "location": "Lumbini Park",
        "restaurant_name": "Mexican Place 49",
        "cuisine_type": "Thai",
        "price_range(per person)": 500,
        "dietary_restrictions": "None",
        "group_size": 10
    },
    {
        "location": "Lumbini Park",
        "restaurant_name": "Chinese Place 32",
        "cuisine_type": "Thai",
        "price_range(per person)": 1000,
        "dietary_restrictions": "None",
        "group_size": 6
    },
    ...
]
```

# Travel Options Data Format

## File: `travel.txt`

## Structure
List of dictionaries, each representing a travel option.

## Dictionary Properties
- `destination`: String (see Locations list)
- `available_time`: Integer (minutes, range depends on preferred_mode)
- `preferred_mode`: String ("walk", "public_transport", or "private_transport")


## Travel Modes and Time Ranges
- walk: 5 to 30 minutes
- public_transport: 10 to 60 minutes
- private_transport: 5 to 40 minutes

## Data Volume
- 15 locations
- 3 travel modes per location
- Total: 45 travel options

## Sample Data
```
{'destination': 'Lumbini Park', 'available_time': 6, 'preferred_mode': 'walk'}
{'destination': 'Lumbini Park', 'available_time': 37, 'preferred_mode': 'public_transport'}
{'destination': 'Lumbini Park', 'available_time': 7, 'preferred_mode': 'private_transport'}
{'destination': 'Hussain Sagar Lake', 'available_time': 26, 'preferred_mode': 'walk'}
{'destination': 'Hussain Sagar Lake', 'available_time': 31, 'preferred_mode': 'public_transport'}
{'destination': 'Hussain Sagar Lake', 'available_time': 34, 'preferred_mode': 'private_transport'}
{'destination': 'KBR National Park', 'available_time': 9, 'preferred_mode': 'walk'}
...
```


# Water Quality Data Format

## File: `water_quality_data.json`

## Structure
JSON array of objects, each representing a water quality measurement.

## Object Properties
- `location`: String (see Locations list)
- `timestamp`: String (format: "YYYY-MM-DDTHH:MM:SS", 5-minute intervals)
- `pH`: Float (6.5 to 8.5, 2 decimal places)
- `Dissolved_Oxygen`: Float (5 to 12 mg/L, 2 decimal places)
- `Conductivity`: Float (500 to 1500 µS/cm, 1 decimal place)
- `Turbidity`: Float (1 to 10 NTU, 1 decimal place)
- `Temperature`: Float (15 to 35 °C, 1 decimal place)


## Data Volume
- 15 locations
- 1000 timestamps per location
- Total: 15,000 records

## Sample Data
```json
[
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:25:28",
        "pH": 8.13,
        "Dissolved_Oxygen": 7.99,
        "Conductivity": 1119.7,
        "Turbidity": 8.0,
        "Temperature": 24.4
    },
    {
        "location": "Lumbini Park",
        "timestamp": "2024-10-22T09:20:28",
        "pH": 7.71,
        "Dissolved_Oxygen": 5.34,
        "Conductivity": 883.8,
        "Turbidity": 3.5,
        "Temperature": 21.4
    },
    ...
]
```


# Exhibition Data Format

## File: `exhibition_data.json`

## Structure
JSON array of objects, each representing an exhibition.

## Object Properties
- `interested_audience`: String (see Interested Audiences list)
- `location`: String (see Locations list)
- `date_range`: String (format: "YYYY-MM-DD - YYYY-MM-DD")
- `exhibition_type`: String (see Exhibition Types list)

## Interested Audiences
Art Lovers, Fashion Enthusiasts, Foodies, Collectors, Tech Buffs


## Data Volume
- 20 exhibition entries

## Note
Date ranges are generated randomly, starting from the current date up to 60 days in the future.
```json
[
    {
        "interested_audience": "Tech Buffs",
        "location": "Hyderabad International Convention Centre",
        "date_range": "2024-11-09 - 2024-12-04",
        "exhibition_type": "Home Decor Exhibition"
    },
    {
        "interested_audience": "Foodies",
        "location": "HITEC City",
        "date_range": "2024-11-02 - 2024-11-26",
        "exhibition_type": "Fashion Show"
    },
    ...
]
```

# Event Ticket Prices Data Format

## File: `event_ticket_prices.csv`

## Complete Data
```csv
Event Name,Ticket Price
Hyderabad Cultural Dance Festival,150
Lumbini Park Laser Light Show,100
Golconda Fort Sound and Light Show,120
Charminar Heritage Walk,80
HITEC City Technology Exhibition,250
Hyderabad International Film Festival,300
Botanical Gardens Nature Photography Contest,50
Hyderabad Crafts Fair at Shilparamam,70
Salar Jung Museum Art Exhibit,100
Bonalu Festival Procession,0
Golconda Fort Medieval Fair,150
Hyderabad Street Food Festival,20
...
```
