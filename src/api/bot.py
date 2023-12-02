from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ApplicationHandlerStop, TypeHandler
from telegram.helpers import escape_markdown
from src.api.aero_api import AeroAPI
from src.api.models import Flight, FlightData
from datetime import datetime, timezone, timedelta

def escape_markdown_2(text: str) -> str:
    return escape_markdown(text, version=2)

def format_timedelta(td: timedelta) -> str:
    """
    Format a timedelta object as H:M.
    """
    total = td.total_seconds()
    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    return f'{hours}:{minutes:02}'

def create_md_message(flight: Flight, flight_data: FlightData) -> str:
    """
    Create a Markdown-formatted message from the current flight data.
    """
    message_parts = [
        f'*{flight.ident}*',
        '\n*Flight details*'
    ]

    if flight.operator is not None:
        message_parts.append(f'*Operator:* {flight.operator}')
    if flight.origin.name is not None:
        message_parts.append(f'*Origin:* {flight.origin.name} \\({flight.origin.code}\\)')
    if flight.destination.name is not None:
        message_parts.append(f'*Destination:* {flight.destination.name} \\({flight.destination.code}\\)')
    if flight.aircraft_type is not None:
        message_parts.append(f'*Aircraft type:* {flight.aircraft_type}')
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
    return '\n'.join(message_parts)


class StatusHandler:

    def __init__(self, api):
        self.api = api

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        message = create_md_message(flight, flight_data)
        await update.message.reply_markdown_v2(message)
        await update.message.reply_location(flight_data.last_position.latitude, flight_data.last_position.longitude)


class AuthHandler:

    def __init__(self, allowed_users):
        self.allowed_users = allowed_users

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = str(update.effective_user.id)
        if user not in self.allowed_users:
            await update.message.reply_text('You are not authorised to use this bot')
            raise ApplicationHandlerStop

class FlightStatusBot:
    def __init__(self, api: AeroAPI, token: str, allowed_users: list[str]):
        self.api = api
        self.token = token
        self.allowed_users = allowed_users

    def get_application(self):
        application = ApplicationBuilder().token(self.token).build()
        auth_handler = AuthHandler(self.allowed_users)
        status_handler = StatusHandler(self.api)
        application.add_handler(TypeHandler(Update, auth_handler.handle), -1)
        application.add_handler(CommandHandler('status', status_handler.handle))
        return application
