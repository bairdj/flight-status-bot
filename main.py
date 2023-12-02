from src.api.aero_api import AeroAPI
from src.api.bot import FlightStatusBot
import os

def get_param_from_env(param_name: str) -> str:
    param = os.environ.get(param_name)
    if param is None:
        raise ValueError(f'{param_name} not set')
    return param

if __name__ == '__main__':
    # Retrieve variables from environment
    aero_api_key = get_param_from_env('AERO_API_KEY')
    telegram_api_key = get_param_from_env('TELEGRAM_API_KEY')
    allowed_users = get_param_from_env('ALLOWED_USERS').split(',')
    
    api = AeroAPI(aero_api_key)
    bot = FlightStatusBot(api, telegram_api_key, allowed_users)

    application = bot.get_application()
    application.run_polling(poll_interval=10)
