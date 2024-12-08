class WaterQualityMonitor(MicroserviceBase):
    def __init__(self):
        super().__init__("water_quality_monitor")
        self.update_service_info(
            description="This service provides real-time water quality monitoring for different locations.",
            dependencies=["uvicorn"]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/water_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/water_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/water_quality_data.json")
            return []

    @staticmethod
    async def find_closest_timestamp(timestamps, target_timestamp):
        timestamps = sorted([dt for dt in timestamps if dt <= target_timestamp], reverse=True)
        if timestamps:
            return timestamps[0]
        else:
            raise ValueError("No suitable timestamp found")

    async def process_request(self, location: str, timestamp: Optional[str] = None) -> dict:
        data_points = next((x for x in self.data if x['location'] == location), None)
        if not data_points:
            raise HTTPException(status_code=404, detail={
               'message': 'Location not found',
            })

        if timestamp:
            timestamp_obj = datetime.datetime.fromisoformat(timestamp)
            target_timestamp = await self.find_closest_timestamp([datetime.datetime.fromisoformat(ts).isoformat() for ts in data_points['timestamp']], timestamp_obj.isoformat())
            closest_point = next((x for x in data_points if x['timestamp'] == target_timestamp), None)
            if not closest_point:
                raise HTTPException(status_code=500, detail={
                   'message': 'Internal server error',
                })
            return {
                'location': location,
                'timestamp': closest_point['timestamp'],
                'pH': closest_point['pH'],
                'Dissolved_Oxygen': closest_point['Dissolved_Oxygen'],
                'Conductivity': closest_point['Conductivity'],
                'Turbidity': closest_point['Turbidity'],
                'Temperature': closest_point['Temperature'],
            }
        else:
            latest_point = max(data_points, key=lambda x: datetime.datetime.fromisoformat(x['timestamp']))
            return {
                'location': latest_point['location'],
                'timestamp': latest_point['timestamp'],
                'pH': latest_point['pH'],
                'Dissolved_Oxygen': latest_point['Dissolved_Oxygen'],
                'Conductivity': latest_point['Conductivity'],
                'Turbidity': latest_point['Turbidity'],
                'Temperature': latest_point['Temperature'],
            }

    def register_routes(self, app):
        app.add_api_route("/query", self.process_request, methods=["POST"])

if __name__ == "__main__":
    WaterQualityMonitor().run()
