# Polar-to-FitTrackee 

Sync activities from flow.polar.com to self-hosted FitTrackee instance

## Setup 

Check and adapt `./config/users/example.json` to get started.

To setup the `polar_access_token` and `polar_user_id` follow the instructions on [polar.com/accesslink-api](https://www.polar.com/accesslink-api/#how-to-get-started). Alternatively, polars [python example](https://github.com/polarofficial/accesslink-example-python) can be used. The required steps are;

1. Login at https://admin.polaraccesslink.com/#/clients 
2. There, create a Client. Note down the Client ID and Client secret (!!)
3. `git clone https://github.com/polarofficial/accesslink-example-python.git`
4. Populate the `config.yml` with the ID and secret. 
5. `uv add -r requirements.txt`
6. `uv run example_web_app.py`
7. Follow the 'Link to authorize'
8. 'Read User Data'
    - `polar-user-id` -> `polar_user_id`
    - `member-id` --> `polar_access_token`
    - Alternatively; see `usertokens.yml`


## Run
To run the script one; `uv run sync.py`

Run with docker compose: `docker compose up`

To add it to crontab (`crontab -e`) best use docker (`sync.py` per default stores to `./data`)

```
*/15 * * * * docker compose -f /<<your-absolute-path>>/polar-to-fittrackee/docker-compose.yml up -d
```
