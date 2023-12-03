from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class FlightAirportRef(BaseModel):
    code: Optional[str] = None
    code_icao: Optional[str] = None
    code_iata: Optional[str] = None
    code_lid: Optional[str] = None
    timezone: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None
    airport_info_url: Optional[str] = None

class AltitudeChange(Enum):
    climb = 'C'
    descent = 'D'
    level = '-'

    # Method to create a nice human readable string to describe the altitude change
    def describe(self):
        if self == AltitudeChange.climb:
            return 'Climbing'
        elif self == AltitudeChange.descent:
            return 'Descending'
        elif self == AltitudeChange.level:
            return 'Level'

class PositionUpdateType(Enum):
    projected = 'P'
    oceanic = 'O'
    radar = 'Z'
    adsb = 'A'
    multilateration = 'M'
    datalink = 'D'
    surface = 'X'
    space = 'S'

class FlightPosition(BaseModel):
    fa_flight_id: Optional[str] = None
    altitude: int
    altitude_change: AltitudeChange
    groundspeed: int
    heading: Optional[int] = None
    latitude: float
    longitude: float
    timestamp: datetime
    update_type: Optional[PositionUpdateType] = None

class Flight(BaseModel):
    ident: str
    ident_icao: Optional[str] = None
    ident_iata: Optional[str] = None
    actual_runway_off: Optional[str] = None
    actual_runway_on: Optional[str] = None
    fa_flight_id: str
    operator: Optional[str] = None
    operator_icao: Optional[str] = None
    operator_iata: Optional[str] = None
    flight_number: Optional[str] = None
    registration: Optional[str] = None
    atc_ident: Optional[str] = None
    inbound_fa_flight_id: Optional[str] = None
    codeshares: List[str]
    codeshares_iata: List[str]
    blocked: bool
    diverted: bool
    cancelled: bool
    position_only: bool
    origin: FlightAirportRef
    destination: FlightAirportRef
    departure_delay: Optional[int] = None
    arrival_delay: Optional[int] = None
    filed_ete: Optional[int] = None
    progress_percent: Optional[int] = None
    status: Optional[str] = None
    aircraft_type: Optional[str] = None
    route_distance: Optional[int] = None
    filed_airspeed: Optional[int] = None
    filed_altitude: Optional[int] = None
    route: Optional[str] = None
    baggage_claim: Optional[str] = None
    seats_cabin_business: Optional[int] = None
    seats_cabin_coach: Optional[int] = None
    seats_cabin_first: Optional[int] = None
    gate_origin: Optional[str] = None
    gate_destination: Optional[str] = None
    terminal_origin: Optional[str] = None
    terminal_destination: Optional[str] = None


class FlightData(BaseModel):
    ident: str
    ident_icao: Optional[str] = None
    ident_iata: Optional[str] = None
    fa_flight_id: str
    origin: FlightAirportRef
    destination: FlightAirportRef
    last_position: FlightPosition
    ident_prefix: Optional[str] = None
    aircraft_type: Optional[str] = None
    actual_off: Optional[datetime] = None
    actual_on: Optional[datetime] = None
    predicted_out: Optional[datetime] = None
    predicted_off: Optional[datetime] = None
    predicted_on: Optional[datetime] = None
    predicted_in: Optional[datetime] = None
