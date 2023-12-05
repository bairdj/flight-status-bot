import os
from src.api import AeroAPI, LocationApi
from src.bot import FlightStatusBot

def get_param_from_env(param_name: str, optional=False) -> str:
    """
    Retrieve a parameter from the environment. If it is not set, raise a ValueError.
    """
    param = os.environ.get(param_name)
    if param is None and not optional:
        raise ValueError(f'{param_name} not set')
    return param

if __name__ == '__main__':
    # Retrieve variables from environment
    aero_api_key = get_param_from_env('AERO_API_KEY')
    telegram_api_key = get_param_from_env('TELEGRAM_API_KEY')
    allowed_users = get_param_from_env('ALLOWED_USERS').split(',')
    locationiq_api_key = get_param_from_env('LOCATIONIQ_API_KEY')

    location_api = LocationApi(locationiq_api_key) if locationiq_api_key is not None else None

    api = AeroAPI(aero_api_key)
    bot = FlightStatusBot(api, telegram_api_key, allowed_users, location_api)

    application = bot.get_application()
    application.run_polling(poll_interval=10)
