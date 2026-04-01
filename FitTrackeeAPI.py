import requests
import json 
import os
import logger as log
from util import load_mapping_json

# https://github.com/SamR1/FitTrackee
# https://docs.fittrackee.org/en/api/index.html

class Client():

    def __init__(self, username, ft_url, ft_email, ft_password, ft_equipment_ids, ft_default_privacy):
        self.username = username
        self.ft_url = ft_url
        self.ft_email = ft_email
        self.ft_password = ft_password
        self.equipment_ids = ft_equipment_ids
        self.auth_token = None
        self.fittrackee2id = load_mapping_json("fittrackee2id")
        self.polar2fittrackee = load_mapping_json("polar2fittrackee")
        self.default_privacy = ft_default_privacy

    def login(self):
        # https://docs.fittrackee.org/en/api/auth.html
        credentials = {"email": self.ft_email, "password": self.ft_password}
        try:
            response = requests.post(f'{self.ft_url}/api/auth/login', json=credentials)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            log.debug(self.username, f"FTC - Login successful! Status Code: {response.status_code}")
            log.debug(self.username, f"FTC - Response JSON: {response.json()}")
            self.auth_token = response.json()['auth_token']
            return True
        except requests.exceptions.HTTPError as e:
            log.debug(self.username, f"FTC - HTTP Error during login: {e}")
            log.debug(self.username, f"FTC - Response content: {e.response.text}")
        except requests.exceptions.RequestException as e:
            log.debug(self.username, f"FTC - An error occurred during the request: {e}")
        return False

    def logout(self):
        # https://docs.fittrackee.org/en/api/auth.html
        try:
            response = requests.post(f'{self.ft_url}/api/auth/logout',
                        headers = {'Authorization': f'Bearer {self.auth_token}'},
                        timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            log.debug(self.username, f"FTC - HTTP Error during logout: {e}")
            log.debug(self.username, f"FTC - Response content: {e.response.text}")
        except requests.exceptions.RequestException as e:
            log.debug(self.username, f"FTC - An error occurred during the request: {e}")
        return False 
    
    def create_workout(self, file_path, mapping):
        # https://docs.fittrackee.org/en/api/workouts.html

        # determine sport_type -- prefer user config and fall back to default mapping
        try:
            sport_type = mapping["sport"]
        except KeyError:
            sport_type = self.polar2fittrackee["sport"]

        try:
            with open(file_path, 'rb') as workout_file:
                response = requests.post(f'{self.ft_url}/api/workouts',
                    headers = {'Authorization': f'Bearer {self.auth_token}'},
                    files = {
                        'file': (
                            os.path.basename(file_path), 
                            workout_file,
                            'application/octet-stream',
                        )
                    },
                    data = {
                        'data': json.dumps(
                            {
                                "sport_id": self.fittrackee2id[sport_type],
                                "notes": "", 
                                "description": "", 
                                "title": mapping.get("title", ""),  
                                "equipment_ids": [self.equipment_ids[x] for x in mapping["equipment"]], 
                                "workout_visibility": mapping.get("privacy", self.default_privacy), 
                                "analysis_visibility": mapping.get("privacy", self.default_privacy),
                                "map_visibility": mapping.get("privacy", self.default_privacy)
                            }
                        )
                    },
                    timeout=30
                )
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                log.debug(self.username, f"FTC - Login successful! Status Code: {response.status_code}")
                log.debug(self.username, f"FTC - Response JSON: {response.json()}")
                return True, response.json()["data"]["workouts"][0]["id"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == "400":
                log.warn(f"FTC - invalid workout file: {file_path}")
                return False, response.status_code
            log.debug(self.username, f"FTC - HTTP Error during workout upload: {e}")
            log.debug(self.username, f"FTC - Response content: {e.response.text}")
        except requests.exceptions.RequestException as e:
            log.debug(self.username, f"FTC - An error occurred during the request: {e}")
        return False, ""

