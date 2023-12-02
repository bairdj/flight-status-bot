import requests
from datetime import datetime, timedelta, timezone
from .models import FlightData, Flight

class ApiError(Exception):
    pass

class AeroAPI:

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'x-apikey': self.api_key})
        self.base_url = 'https://aeroapi.flightaware.com/aeroapi'

    def get_flight(self, ident):
        """
        Retrieve a FlightAware flight for a given flight number.

        The API returns previous and scheduled flights. This function aims
        to identify only the current flight in the air that matches the identifier.
        If the flight is not currently in the air, it will return None.

        @param ident: Flight number in either ICAO or IATA format (e.g. 'QFA10')
        @return: Flight object
        """
        endpoint = f'{self.base_url}/flights/{ident}'
        # Scheduled out (gate departure) must be 24 hours either side of now
        # This gives some leeway for delayed flights
        current_time = datetime.now(timezone.utc)
        scheduled_out_start = current_time - timedelta(hours=24)
        scheduled_out_end = current_time + timedelta(hours=24)
        params = {
            'start': scheduled_out_start.isoformat(timespec='seconds'),
            'end': scheduled_out_end.isoformat(timespec='seconds')
        }
        response = self.session.get(endpoint, params=params)
        if response.status_code != 200:
            raise ApiError(f'GET {endpoint} returned {response.status_code}')
        flights = response.json()['flights']
        # Flights currently in the air will have an actual runway departure time
        # and no actual runway arrival time
        in_air = [f for f in flights if f['actual_off'] is not None and f['actual_on'] is None]
        if len(in_air) != 1:
            return None
        return Flight.model_validate(in_air[0])

    def get_flight_data(self, flight_id):
        """
        Get the current position and other data for a flight.

        @param flight_id: FlightAware unique ID (e.g. 'QFA9-1701256998-schedule-2186p')
        @return: FlightData object
        """
        endpoint = f'{self.base_url}/flights/{flight_id}/position'
        response = self.session.get(endpoint)
        if response.status_code != 200:
            raise ApiError(f'GET {endpoint} returned {response.status_code}')
        return FlightData.model_validate_json(response.content)
