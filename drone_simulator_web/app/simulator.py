import time
import math
import random
import numpy as np
from haversine import haversine, Unit
from enum import Enum

LOCATIONS = {
    "madrid": {"name": "Madrid", "coordinates": (40.471926, -3.562599), "max_altitude": 120},
    "munich": {"name": "Múnich", "coordinates": (48.353889, 11.786111), "max_altitude": 150},
    "tenerife": {"name": "Tenerife", "coordinates": (28.044444, -16.5725), "max_altitude": 300}
}

class Mode(Enum):
    ON_GROUND = 1
    TAKING_OFF = 2
    CRUISING = 3
    RETURNING_HOME = 4
    LANDING = 5
    EMERGENCY_LANDING = 6

class DroneSimulator:
    def __init__(self, location_config):
        self.base_lat, self.base_lon = location_config["coordinates"]
        self.current_pos = (self.base_lat, self.base_lon)
        self.altitude = 0.0
        self.speed = 0.0
        self.battery = 100.0
        self.mode = Mode.ON_GROUND
        self.last_update = time.time()
        self.max_altitude = location_config["max_altitude"]
        self.cruise_altitude = 0.8 * self.max_altitude
        self.patrol_radius = 500  # metros
        self.cruise_speed = 15  # m/s
        self.angle = 0
        self.gps_error = 4.5e-6
        self.location_name = location_config["name"]

    def _add_gps_noise(self, position):
        noise_lat = position[0] + np.random.normal(0, self.gps_error)
        noise_lon = position[1] + np.random.normal(0, self.gps_error)
        return (noise_lat, noise_lon)

    def _update_battery(self):
        elapsed = time.time() - self.last_update
        if self.mode == Mode.ON_GROUND:
            drain = 0.01 * elapsed
        elif self.mode == Mode.TAKING_OFF:
            drain = 0.2 * elapsed
        elif self.mode in [Mode.CRUISING, Mode.RETURNING_HOME]:
            drain = (0.1 + 0.01 * self.speed) * elapsed
        elif self.mode == Mode.LANDING:
            drain = 0.15 * elapsed
        elif self.mode == Mode.EMERGENCY_LANDING:
            drain = 0.3 * elapsed
        else:
            drain = 0
        self.battery -= drain
        self.battery = max(self.battery, 0)

    def _update_altitude(self, rate):
        elapsed = time.time() - self.last_update
        self.altitude += rate * elapsed
        if rate > 0:
            self.altitude = min(self.altitude, self.cruise_altitude)
        else:
            self.altitude = max(self.altitude, 0)

    def _update_position_cruising(self):
        elapsed = time.time() - self.last_update
        angular_speed = self.cruise_speed / self.patrol_radius
        self.angle += angular_speed * elapsed
        delta_lat = (self.patrol_radius / 111320) * math.sin(self.angle)
        delta_lon = (self.patrol_radius / (111320 * math.cos(math.radians(self.base_lat)))) * math.cos(self.angle)
        self.current_pos = (self.base_lat + delta_lat, self.base_lon + delta_lon)
        self.speed = self.cruise_speed

    def _update_position_returning_home(self):
        elapsed = time.time() - self.last_update
        dx = self.base_lat - self.current_pos[0]
        dy = self.base_lon - self.current_pos[1]
        distance = haversine(self.current_pos, (self.base_lat, self.base_lon), unit=Unit.METERS)
        if distance < self.cruise_speed * elapsed:
            self.current_pos = (self.base_lat, self.base_lon)
            self.mode = Mode.LANDING
        else:
            fraction = (self.cruise_speed * elapsed) / distance
            new_lat = self.current_pos[0] + fraction * dx
            new_lon = self.current_pos[1] + fraction * dy
            self.current_pos = (new_lat, new_lon)
        self.speed = self.cruise_speed if distance > 0 else 0

    def generate_data(self):
        self._update_battery()
        if self.mode == Mode.ON_GROUND:
            self.mode = Mode.TAKING_OFF
        elif self.mode == Mode.TAKING_OFF:
            self._update_altitude(1.5)
            if self.altitude >= self.cruise_altitude:
                self.mode = Mode.CRUISING
        elif self.mode == Mode.CRUISING:
            self._update_position_cruising()
        elif self.mode == Mode.RETURNING_HOME:
            self._update_position_returning_home()
        elif self.mode == Mode.LANDING:
            self._update_altitude(-1.0)
            if self.altitude <= 0:
                self.mode = Mode.ON_GROUND
        elif self.mode == Mode.EMERGENCY_LANDING:
            self._update_altitude(-3.0)
            if self.altitude <= 0:
                self.mode = Mode.ON_GROUND

        if self.battery <= 10 and self.mode != Mode.EMERGENCY_LANDING:
            self.mode = Mode.EMERGENCY_LANDING
        elif self.battery <= 20 and self.mode not in [Mode.RETURNING_HOME, Mode.LANDING, Mode.EMERGENCY_LANDING, Mode.ON_GROUND]:
            self.mode = Mode.RETURNING_HOME

        self.last_update = time.time()
        noisy_position = self._add_gps_noise(self.current_pos)

        return {
            "timestamp": time.time(),
            "latitude": noisy_position[0],
            "longitude": noisy_position[1],
            "altitude": self.altitude,
            "speed": self.speed,
            "battery": self.battery,
            "status": self.mode.name,
            "health_check": "OK" if random.random() > 0.02 else "WARNING",
            "location": self.location_name,
            "max_altitude": self.max_altitude
        }
