import os
from dotenv import load_dotenv
import logger as log
from util import load_user_json, load_mapping_json

import PolarFlowAPI
import FitTrackeeAPI

if __name__ == "__main__":

    load_dotenv("./config/.env")

    for user in [u.replace(".json","") for u in os.listdir("./config/users") if u != "example.json"]:

        ## Create user_data_dir if not existing already
        os.makedirs("./data", exist_ok=True)
        user_data_dir = f"./data/{user}"
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(f"{user_data_dir}/archive", exist_ok=True)
        os.makedirs(f"{user_data_dir}/failed", exist_ok=True)
        os.makedirs(f"{user_data_dir}/no-mapping", exist_ok=True)

        ## Load user config
        user_config = load_user_json(user)

        ## Setup PolarFlowClient
        polar_access_token = user_config["polar_access_token"]
        polar_user_id = user_config["polar_user_id"]
        PFC = PolarFlowAPI.Client(user, polar_access_token, polar_user_id, user_data_dir)

        ## Collect new Workouts from Polar
        PFC.collect_workouts()

        ## Setup FitTrackeeClient
        try:
            ft_url = user_config["fittrackee_url"]
        except KeyError:
            ft_url = os.getenv("FITTRACKEE_DEFAULT_URL", "")
            if not ft_url:
                raise Exception("FitTrackee URL is not provided. Neither in global nor in user config.")
        ft_email = user_config["fittrackee_email"]
        ft_password = user_config["fittrackee_password"]
        ft_equipment_ids = user_config["fittrackee_equipment_ids"]
        ft_default_privacy = user_config["fittrackee_default_privacy"]

        FTC = FitTrackeeAPI.Client(user, ft_url, ft_email, ft_password, ft_equipment_ids, ft_default_privacy)
        if not FTC.login():
            break

        polar_user_mapping = user_config["mapping_polar"]
        polar_default_mapping = load_mapping_json("polar2fittrackee")


        ## Upload all available files to Fittrackee
        for fname in os.listdir(user_data_dir):
            if ".tcx" not in fname and ".fit" not in fname:
                continue

            polar_activity_type = fname[20:-4]  # ([0:19] is timestamp)
            if polar_activity_type in polar_user_mapping.keys():
                map = polar_user_mapping[polar_activity_type]
            elif polar_activity_type in polar_default_mapping.keys():
                map = polar_default_mapping[polar_activity_type]
            else:
                os.rename(f"{user_data_dir}/{fname}", f"{user_data_dir}/no-mapping/{fname}")
                log.info(user, f"SYNC: no mapping for \"{fname[:-4]}\" - skipping")
                continue
            
            ## Upload Workout to FitTrackee
            success, ftc_id = FTC.create_workout(f"{user_data_dir}/{fname}", map)
            if success:
                os.rename(f"{user_data_dir}/{fname}", f"{user_data_dir}/archive/{fname}")
                log.info(user, f"{ftc_id} \"{fname[:-4]}\" - {map}")
            else:
                os.rename(f"{user_data_dir}/{fname}", f"{user_data_dir}/failed/{fname}")
                log.info(user, f"upload of {fname[:-4]} failed")

        FTC.logout()
