| Service            | Description                                                            | Input Parameters                                                                                                                                                 |
| ------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| travel_options     | Provides transportation options and routes to tourist destinations     | user_location, destination, available_time, preferred_mode                                                                                                       |
| crowd_monitor      | Tracks and reports real-time crowd density at various locations        | location_name, time_of_day, day_of_week, event_nearby                                                                                                            |
| event_notifier     | Sends notifications about upcoming events, shows, and festivals        | None                                                                                                                                                             |
| historical_info    | Provides historical and cultural information about monuments and sites | site_name                                                                                                                                                        |
| air_quality        | Monitors and reports air quality levels in different areas             | locations                                                                                                                                                        |
| water_quality      | Tracks water quality in lakes and other water bodies                   | water_body_name                                                                                                                                                  |
| restaurant_finder  | Recommends restaurants based on cuisine preferences and location       | user_location, cuisine_type, price_range, dietary_restrictions, group_size                                                                                       |
| ticket_purchase    | Enables online ticket purchases for attractions and events             | ticket_type                                                                                                                                                      |
| exhibition_tracker | Tracks and notifies users about ongoing and upcoming exhibitions       | user_interests, user_location, date_range, exhibition_type                                                                                                       |

### parameter values

#### travel_options
- user_location: "latitude,longitude" (ex: "17.3850,78.4867")
- destination: "landmark name" or "latitude,longitude"
- available_time: integer (minutes)
- preferred_mode: ["walk", "public_transport", "private_transport"]

#### crowd_monitor
- location_name: string (ex: "charminar", "hussain sagar")
- time_of_day: "hh:mm" (24-hour format)
- day_of_week: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
- event_nearby: boolean

#### event_notifier
- nil (:P)

#### historical_info
- site_name: string (ex: "charminar")

#### air_quality
- locations: list of strings (ex: ["hyderabad", "secunderabad", "cyberabad"])

#### water_quality
- water_body_name: string (ex: "hussain sagar", "osman sagar", "himayat sagar")

#### restaurant_finder
- user_location: "latitude,longitude"
- cuisine_type: ["hyderabadi", "south indian", "north indian", "chinese", "continental"]
- price_range: tuple of 2 integers (ex: (1000, 2000)) // any better suggestions here?
- dietary_restrictions: ["vegetarian", "vegan", "halal ;)", "none"]
- group_size: integer

#### ticket_purchase
- ticket_type: ["movie", "concert", "monument", "museum", "theme_park"]

#### exhibition_tracker
- user_interests: ["art", "history", "science", "technology", "culture"]
- user_location: "latitude,longitude"
- date_range: "yyyy-mm-dd,yyyy-mm-dd"
- exhibition_type: ["art", "historical", "scientific", "cultural", "interactive"]
