from typing import Callable, Awaitable
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ApplicationHandlerStop,
    TypeHandler,
    Application,
    CallbackContext
)
from telegram.helpers import escape_markdown
from src.api import AeroAPI, LocationApi
from src.models import Flight, FlightData

def escape_markdown_2(text: str) -> str:
    """
    Wrapper around telegram.helpers.escape_markdown to use version 2 of the API.
    """
    return escape_markdown(text, version=2)

def format_timedelta(td: timedelta) -> str:
    """
    Format a timedelta object as H:M.
    """
    total = td.total_seconds()
    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    return f'{hours}:{minutes:02}'

def create_md_message(flight: Flight, flight_data: FlightData, geocoded_location: str = None) -> str:
    """
    Create a Markdown-formatted message from the current flight data.
    """
    message_parts = [
        f'*{flight.ident}*',
        '\n*Flight details*'
    ]

    if flight.operator is not None:
        message_parts.append(f'*Operator:* {escape_markdown_2(flight.operator)}')
    if flight.origin.name is not None:
        message_parts.append(f'*Origin:* {escape_markdown_2(flight.origin.name)} \\({flight.origin.code}\\)')
    if flight.destination.name is not None:
        message_parts.append(f'*Destination:* {escape_markdown_2(flight.destination.name)} \\({flight.destination.code}\\)')
    if flight.aircraft_type is not None:
        message_parts.append(f'*Aircraft type:* {escape_markdown_2(flight.aircraft_type)}')
    if flight.registration is not None:
        message_parts.append(f'*Registration:* {escape_markdown_2(flight.registration)}')
    if flight.actual_runway_off is not None:
        message_parts.append(f'*Take off runway:* {flight.actual_runway_off}')
    if flight.actual_runway_on is not None:
        message_parts.append(f'*Landing runway:* {flight.actual_runway_on}')

    message_parts.append('\n*Times*')
    if flight_data.actual_off is not None:
        message_parts.append(f'*Take off:* {flight_data.actual_off:%H:%M} UTC')
    if flight_data.predicted_on is not None:
        message_parts.append(f'*Predicted landing:* {flight_data.predicted_on:%H:%M} UTC')
        time_to_go = flight_data.predicted_on - datetime.now(timezone.utc)
        if time_to_go > timedelta(minutes=0):
            message_parts.append(f'*Time to landing:* {format_timedelta(time_to_go)}')

    message_parts.append('\n*Flight status*')
    message_parts.append(f'*Altitude*: {flight_data.last_position.altitude * 100} ft')
    message_parts.append(f'*Ground speed*: {flight_data.last_position.groundspeed} kts')
    if flight_data.last_position.heading is not None:
        message_parts.append(f'*Heading*: {flight_data.last_position.heading}°')
    message_parts.append(f'*Flight phase*: {flight_data.last_position.altitude_change.describe()}')

    if geocoded_location is not None:
        message_parts.append(f'*Location*: Near {geocoded_location}')
    return '\n'.join(message_parts)

class FlightStatusBot:
    """
    A Telegram bot for checking flight status.

    This bot uses the AeroAPI to fetch flight data and responds to user commands on Telegram.
    It supports a command for checking the status of a flight.

    Only users with IDs in the `allowed_users` list are authorised to use the bot.

    :param api: An instance of AeroAPI to fetch flight data.
    :param bot_token: The token for the Telegram bot.
    :param allowed_users: A list of Telegram user IDs that are allowed to use the bot.
    """
    def __init__(self, api: AeroAPI, bot_token: str, allowed_users: list[str], location_api: LocationApi = None):
        """
        Create a new bot instance.

        :param api: The AeroAPI instance to use.
        :param bot_token: The Telegram bot token.
        :param allowed_users: A list of Telegram user IDs that are allowed to use the bot.
        """
        self.api = api
        self.bot_token = bot_token
        self.allowed_users = allowed_users
        self.location_api = location_api

    def get_application(self) -> Application:
        """
        Set up the Telegram Application instance.

        :return: The Application instance.
        """
        application = ApplicationBuilder().token(self.bot_token).build()
        application.add_handler(TypeHandler(Update, self._get_auth_handler()), -1)
        application.add_handler(CommandHandler('status', self._get_status_handler()))
        return application

    def _get_auth_handler(self) -> Callable[[Update, CallbackContext], Awaitable[None]]:
        """
        Callback function to check if the user is authorised.
        """
        async def auth_handler(update: Update, context: CallbackContext):
            user = str(update.effective_user.id)
            if user not in self.allowed_users:
                await update.message.reply_text('You are not authorised to use this bot')
                raise ApplicationHandlerStop
        return auth_handler

    def _get_status_handler(self) -> Callable[[Update, CallbackContext], Awaitable[None]]:
        """
        Callback function for the /status command.
        """
        async def status_handler(update: Update, context: CallbackContext):
            args = context.args
            # Should be a single ident
            if len(args) != 1:
                await update.message.reply_text('Usage: /status <flight number>')
                return
            flight_number = args[0]
            flight = self.api.get_flight(flight_number)
            if flight is None:
                await update.message.reply_text('Flight not found')
                return
            flight_data = self.api.get_flight_data(flight.fa_flight_id)
            geocoded_location = None
            if self.location_api is not None:
                geocoded_location = self.location_api.geocode_location(
                    flight_data.last_position.latitude,
                    flight_data.last_position.longitude
                )
            message = create_md_message(flight, flight_data, geocoded_location)
            await update.message.reply_markdown_v2(message)
            await update.message.reply_location(
                latitude=flight_data.last_position.latitude,
                longitude=flight_data.last_position.longitude
            )

        return status_handler
