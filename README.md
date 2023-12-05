# Flight Status Bot

This Telegram bot is a simple wrapper around FlightAware's AeroAPI that retrieves real-time
information about a flight that is currently in the air.

![Example bot usage](/assets/screenshots/example.jpg)

The rationale behind this bot is to allow for detailed flight tracking while using minimal
bandwidth. This is useful if using in-flight WiFi, especially if using a cheaper "messaging only"
plan which is heavily throttled (or filtered) and doesn't allow for loading of a full flight tracking
app/website like FlightAware or FlightRadar24. The data provided by the bot can be more detailed
than what is provided by the airline's IFE system.

The bot is intended to be self-hosted for individual use.


## Setup

The bot uses FlightAware's AeroAPI v4. You need to create an API key via the [portal](https://www.flightaware.com/aeroapi/portal/).

You must also have a Telegram bot token. See details [here](https://core.telegram.org/bots/features#creating-a-new-bot).

You should also obtain your own Telegram chat ID to restrict the bot to your own chat. Bots are otherwise publicly
accessible and could allow others to use your API key and incur costs.

Optionally, the bot can use the [LocationIQ](https://locationiq.com/) API to reverse geocode the current location
to a labelled region. This also works with naming the ocean that the flight is currently over, if applicable.


## Running

The bot can be run using Docker. You must supply environment variables for the AeroAPI key, Telegram bot token
and Telegram chat ID.

Multiple chat IDs can be supplied, separated by commas.

The bot runs using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) using polling
with a 10 second interval.

To run the bot using Docker:

```bash
docker run -e AERO_API_KEY=your_key -e TELEGRAM_API_KEY=your_token -e ALLOWED_USERS=your_chat_id ghcr.io/bairdj/flight-status-bot:main
```

The bot can also be run using Docker Compose:

```yaml
version: "3"
services:
  flight_status_bot:
    image: ghcr.io/bairdj/flight-status-bot:main
    environment:
      AERO_API_KEY: your_key
      TELEGRAM_API_KEY: your_token
      ALLOWED_USERS: your_chat_id
      LOCATIONIQ_API_KEY: your_key # Optional
    restart: unless-stopped
```

## Usage

To use the bot, send a message in the format `/status <flight_number>`. For example:

```
/status QFA10
```

AeroAPI can detect both ICAO and IATA flight numbers. If there is no flight currently in the
air matching the flight number, the bot will respond that the flight cannot be found.
