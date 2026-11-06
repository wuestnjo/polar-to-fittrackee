import requests
import json 
import os
import logger as log

# https://github.com/SamR1/FitTrackee
# https://docs.fittrackee.org/en/api/index.html

FTC_IDS = {
    "Canoeing": 20,
    "Canoeing (Whitewater)": 26,
    "Cycling (Sport)": 1,
    "Cycling (Transport)": 2,
    "Cycling (Trekking)": 17,
    "Cycling (Virtual)": 13,
    "Halfbike": 21,
    "Hiking": 3,
    "Kayaking": 19,
    "Kayaking (Whitewater)": 27,
    "Mountain Biking": 4,
    "Mountain Biking (Electric)": 7,
    "Mountaineering": 14,
    "Open Water Swimming": 16,
    "Paragliding": 15,
    "Rowing": 11,
    "Running": 5,
    "Skiing (Alpine)": 9,
    "Skiing (Cross Country)": 10,
    "Snowshoes": 12,
    "Standup Paddleboarding": 23,
    "Swimrun": 18,
    "Trail": 8,
    "Walking": 6,
    "Windsurfing": 22
}

class Client():

    def __init__(self, username, ft_url, ft_email, ft_password, ft_equipment_ids, ft_default_privacy):
        self.username = username
        self.ft_url = ft_url
        self.ft_email = ft_email
        self.ft_password = ft_password
        self.equipment_ids = ft_equipment_ids
        self.session = requests.Session()
        self.default_privacy = ft_default_privacy

    def login(self):
        # https://docs.fittrackee.org/en/api/auth.html
        credentials = {"email": self.ft_email, "password": self.ft_password}
        try:
            # The token is no longer part of the response body. FitTrackee sets it as
            # 'access_token_cookie' (+ 'csrf_access_token'), which the session keeps.
            response = self.session.post(f'{self.ft_url}/api/auth/login', json=credentials, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            log.debug(self.username, f"FTC - Login successful! Status Code: {response.status_code}")
            log.debug(self.username, f"FTC - Response JSON: {response.json()}")
            if 'access_token_cookie' not in self.session.cookies:
                log.debug(self.username, "FTC - Login response did not set an access token cookie")
                return False
            return True
        except requests.exceptions.HTTPError as e:
            log.debug(self.username, f"FTC - HTTP Error during login: {e}")
            log.debug(self.username, f"FTC - Response content: {e.response.text}")
        except requests.exceptions.RequestException as e:
            log.debug(self.username, f"FTC - An error occurred during the request: {e}")
        return False

    def _auth_headers(self):
        # Cookie based auth (no 'Authorization' header, that one is reserved for OAuth2 tokens).
        # State changing requests must echo the CSRF cookie. Read it per request, since
        # FitTrackee refreshes the cookies shortly before the token expires.
        return {'X-CSRF-TOKEN': self.session.cookies.get('csrf_access_token', '')}

    def logout(self):
        # https://docs.fittrackee.org/en/api/auth.html
        try:
            response = self.session.post(f'{self.ft_url}/api/auth/logout',
                        headers = self._auth_headers(),
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
        try:
            with open(file_path, 'rb') as workout_file:
                response = self.session.post(f'{self.ft_url}/api/workouts',
                    headers = self._auth_headers(),
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
                                "sport_id": FTC_IDS[mapping["sport"]],
                                "notes": "", 
                                "description": "", 
                                "title": mapping.get("title", ""),  
                                "equipment_ids": [self.equipment_ids[x] for x in mapping.get("equipment", [])], 
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

