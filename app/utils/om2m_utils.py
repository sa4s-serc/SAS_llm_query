import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class OM2MManager:
    def __init__(self, base_url: str = "http://127.0.0.1:8080", credentials: str = "admin:admin"):
        self.base_url = base_url
        self.credentials = credentials
        self.sensors = [
            "airSensor",
            "waterSensor",
            "solarSensor",
            "crowdmonSensor",
            "weatherSensor",
            "roommonSensor"
        ]

    def check_cse_exists(self) -> bool:
        """Check if the base CSE (in-name) exists"""
        url = f"{self.base_url}/~/in-cse/in-name/"
        headers = {
            "X-M2M-Origin": self.credentials,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Error checking CSE: {str(e)}")
            return False

    def create_ae(self, sensor_name: str) -> Optional[str]:
        """Create an Application Entity (AE) for a specific sensor"""
        if not self.check_cse_exists():
            logger.error("Base CSE not found")
            return None

        url = f"{self.base_url}/~/in-cse/in-name/"
        headers = {
            "X-M2M-Origin": self.credentials,
            "Content-Type": "application/json;ty=2"
        }
        payload = {
            "m2m:ae": {
                "rn": sensor_name,
                "api": "N_SensorData",
                "rr": True,
                "lbl": ["Type/sensor", f"Category/{sensor_name}"]
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                logger.info(f"Application Entity created for {sensor_name}")
                return response.json()["m2m:ae"]["ri"]
            else:
                logger.error(f"Failed to create AE for {sensor_name}. Status: {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error creating AE: {str(e)}")
            return None

    def create_container(self, ae_name: str, container_name: str = "data") -> bool:
        """Create a container inside the specified Application Entity (AE)"""
        url = f"{self.base_url}/~/in-cse/in-name/{ae_name}"
        headers = {
            "X-M2M-Origin": self.credentials,
            "Content-Type": "application/json;ty=3"
        }
        payload = {
            "m2m:cnt": {
                "rn": container_name,
                "mni": 1000  # Maximum number of instances
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                logger.info(f"Container {container_name} created for {ae_name}")
                return True
            else:
                logger.error(f"Failed to create container for {ae_name}. Status: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Error creating container: {str(e)}")
            return False

    def create_sensor_structure(self, sensor_name: str) -> Dict:
        """Create complete structure for a sensor including AE and containers"""
        result = {
            "sensor": sensor_name,
            "ae_created": False,
            "containers": {}
        }

        # Create AE
        ae_id = self.create_ae(sensor_name)
        if ae_id:
            result["ae_created"] = True
            result["ae_id"] = ae_id

            # Create main data container
            data_container = self.create_container(sensor_name, "data")
            result["containers"]["data"] = data_container

            # Create metadata container
            metadata_container = self.create_container(sensor_name, "metadata")
            result["containers"]["metadata"] = metadata_container

        return result

    def setup_all_sensors(self) -> List[Dict]:
        """Set up all sensor structures"""
        results = []
        for sensor in self.sensors:
            result = self.create_sensor_structure(sensor)
            results.append(result)
        return results

    def get_sensor_data(self, sensor_name: str, container: str = "data") -> Optional[Dict]:
        """Retrieve latest data from a sensor's container"""
        url = f"{self.base_url}/~/in-cse/in-name/{sensor_name}/{container}/la"
        headers = {
            "X-M2M-Origin": self.credentials,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get data for {sensor_name}. Status: {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error getting sensor data: {str(e)}")
            return None

    def delete_sensor_structure(self, sensor_name: str) -> bool:
        """Delete a sensor's complete structure"""
        url = f"{self.base_url}/~/in-cse/in-name/{sensor_name}"
        headers = {
            "X-M2M-Origin": self.credentials
        }

        try:
            response = requests.delete(url, headers=headers)
            return response.status_code in [200, 204]
        except requests.RequestException as e:
            logger.error(f"Error deleting sensor structure: {str(e)}")
            return False 