import requests
import json
import logger as log

# https://www.polar.com/accesslink-api/#introduction


class Client():

    def __init__(self, username, access_token, user_id, data_dir):
        self.username = username
        self.access_token = access_token
        self.user_id = user_id
        self.data_dir = data_dir


    def collect_workouts(self):

        ## get transaction ID of new workouts 
        r = requests.post(
            f'https://www.polaraccesslink.com/v3/users/{self.user_id}/exercise-transactions',
            headers = {'Accept': 'application/json', 'Authorization': f'Bearer {self.access_token}'},
            timeout=10)
        if r.status_code == 201:
            transaction_id = json.loads(r.content)['transaction-id']
        else:
            if r.status_code == 204:
                log.debug(self.username, "PFC - no new content available")
            elif r.status_code == 403:
                log.warn(self.username, "PFC - authentication failed - aborting")
            else:
                log.warn(self.username, f"PFC - api changed !! - unforseen status code: {r.status_code} - aborting")
            return

        ## list exercises
        r = requests.get(
            f'https://www.polaraccesslink.com/v3/users/{self.user_id}/exercise-transactions/{transaction_id}',
            headers = {'Accept': 'application/json',  'Authorization': f'Bearer {self.access_token}'},
            timeout=10)
        if r.status_code == 200:
            exercise_urls = json.loads(r.content)['exercises']
        else:
            return

        ## get exercise summary
        for exercise_url in exercise_urls:
            r = requests.get(
                exercise_url,
                headers = {'Accept': 'application/json',  'Authorization': f'Bearer {self.access_token}'},
                timeout=10)
            if r.status_code == 200:

                ## collect metadata
                content = json.loads(r.content)
                polarID = content['id']
                deviceID = content['device-id']
                activityType = content['detailed-sport-info']
                timestamp = content['start-time']

                ## download tcx
                fname = f"{timestamp}-{activityType}.tcx"
                tcx_file = requests.get(
                    f'{exercise_url}/tcx', 
                    headers = {'Accept': 'application/vnd.garmin.tcx+xml',  'Authorization': f'Bearer {self.access_token}'},
                    timeout=10)
                if tcx_file.status_code == 200:
                    filePath = f"{self.data_dir}/{fname}"
                    with open(filePath, 'wb') as f:
                        f.write(tcx_file.content)
                        log.debug(self.username, f"PFC - {fname} - Downloaded {int(len(tcx_file.content)/1024)} kbytes")
                else:
                    log.warn(self.username, f"PFC - {fname} - Failed with code: {tcx_file.status_code}")

        ## commit transaction
        r = requests.put(
            f'https://www.polaraccesslink.com/v3/users/{self.user_id}/exercise-transactions/{transaction_id}',
            headers = {'Accept': 'application/json',  'Authorization': f'Bearer {self.access_token}'},
            timeout=10)
