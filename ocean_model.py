"""
Synthetic ocean / cyclone physics and lossy-link models.

Used by the sensor simulator, the satellite station, model training and
the offline evaluation so that every component sees the *same* kind of
data. Real buoy datasets (e.g. INCOIS / NOAA NDBC) can replace this later.

Cyclone model
    A vortex approaches the node at a constant speed, passes over it and
    recedes. Wind follows a modified Rankine profile and pressure follows
    the Holland (1980) profile, both functions of distance to the eye.
    On top of that: AR(1) gusts, a diurnal temperature cycle and rain
    cooling near the storm.

Link model
    Gilbert-Elliott two-state Markov channel: a "good" state with rare
    losses and a "bad" (rain fade / interference) state with heavy losses.
    This produces the *bursty* loss real marine/satellite links show,
    unlike independent coin-flip losses.
"""
import math
import random
from dataclasses import dataclass


@dataclass
class CycloneParams:
    onset_step: int = 20          # step at which the cyclone starts moving in
    start_distance_km: float = 600.0
    speed_km_per_step: float = 10.0
    closest_km: float = 25.0      # closest approach (0 = eye passes overhead)
    v_max_kmh: float = 140.0      # max sustained wind at the radius of max wind
    r_max_km: float = 40.0        # radius of maximum wind
    central_pressure_hpa: float = 955.0
    env_pressure_hpa: float = 1010.0
    holland_b: float = 1.5
    enabled: bool = True


@dataclass
class OceanState:
    base_wind: float = 15.0
    base_temp: float = 28.0
    gust: float = 0.0
    pressure_noise: float = 0.0


class OceanNode:
    """Generates one reading per step for a single buoy / radar."""

    def __init__(self, params=None, seed=None, steps_per_day=240):
        self.p = params or CycloneParams()
        self.rng = random.Random(seed)
        self.state = OceanState(base_wind=self.rng.uniform(10, 20), base_temp=self.rng.uniform(26.5, 29.5))
        self.steps_per_day = steps_per_day
        self.t = 0

    def distance_km(self, t):
        p = self.p
        if not p.enabled or t < p.onset_step:
            return p.start_distance_km
        along = p.start_distance_km - p.speed_km_per_step * (t - p.onset_step)
        return math.hypot(along, p.closest_km)

    def cyclone_wind(self, r):
        p = self.p
        r = max(r, 1.0)
        if r <= p.r_max_km:
            return p.v_max_kmh * r / p.r_max_km
        return p.v_max_kmh * (p.r_max_km / r) ** 0.6

    def cyclone_pressure(self, r):
        p = self.p
        r = max(r, 1.0)
        dp = p.env_pressure_hpa - p.central_pressure_hpa
        return p.central_pressure_hpa + dp * math.exp(-((p.r_max_km / r) ** p.holland_b))

    def step(self):
        """Advance one time step and return (wind km/h, temp C, pressure hPa)."""
        s, rng = self.state, self.rng
        r = self.distance_km(self.t)
        far = self.p.start_distance_km

        # Storm contribution relative to its value at the starting distance,
        # so the pre-onset baseline is unaffected.
        storm_wind = max(0.0, self.cyclone_wind(r) - self.cyclone_wind(far)) if self.p.enabled else 0.0
        storm_dp = (self.cyclone_pressure(far) - self.cyclone_pressure(r)) if self.p.enabled else 0.0

        s.gust = 0.85 * s.gust + rng.gauss(0, 1.2 + 0.02 * storm_wind)
        s.base_wind = min(25.0, max(5.0, s.base_wind + rng.gauss(0, 0.15)))
        wind = max(0.0, s.base_wind + storm_wind + s.gust)

        s.pressure_noise = 0.9 * s.pressure_noise + rng.gauss(0, 0.15)
        pressure = self.p.env_pressure_hpa - storm_dp + s.pressure_noise

        diurnal = 0.8 * math.sin(2 * math.pi * self.t / self.steps_per_day)
        rain_cooling = 2.5 * math.exp(-r / 150.0) if self.p.enabled else 0.0
        temp = s.base_temp + diurnal - rain_cooling + rng.gauss(0, 0.05)

        self.t += 1
        return wind, temp, pressure

    def trace(self, n):
        return [self.step() for _ in range(n)]


def random_cyclone_params(rng, n_steps):
    """Randomised scenario for training/evaluation."""
    return CycloneParams(
        onset_step=rng.randint(0, max(1, n_steps // 3)),
        start_distance_km=rng.uniform(400, 800),
        speed_km_per_step=rng.uniform(4, 14),
        closest_km=rng.uniform(0, 120),
        v_max_kmh=rng.uniform(90, 200),
        r_max_km=rng.uniform(25, 60),
        central_pressure_hpa=rng.uniform(930, 985),
        enabled=rng.random() > 0.15,  # some calm-weather traces too
    )


class GilbertElliottLink:
    """
    Bursty packet-loss channel. `mean_loss` is the long-run loss rate;
    `burstiness` (0..1) controls how clustered losses are.
    """

    def __init__(self, mean_loss=0.1, burstiness=0.7, seed=None):
        self.rng = random.Random(seed)
        self.bad = False
        self.loss_good = mean_loss * 0.2
        self.loss_bad = min(0.95, 0.5 + 0.45 * burstiness)
        # Fraction of time in the bad state needed to hit the requested mean.
        denom = self.loss_bad - self.loss_good
        pi_bad = 0.0 if denom <= 0 else min(0.95, max(0.0, (mean_loss - self.loss_good) / denom))
        # Expected bad-burst length grows with burstiness.
        self.p_bad_to_good = max(0.05, 1.0 - burstiness * 0.85)
        self.p_good_to_bad = 0.0 if pi_bad <= 0 else min(0.95, self.p_bad_to_good * pi_bad / (1 - pi_bad))

    def lost(self):
        if self.bad:
            if self.rng.random() < self.p_bad_to_good:
                self.bad = False
        elif self.rng.random() < self.p_good_to_bad:
            self.bad = True
        return self.rng.random() < (self.loss_bad if self.bad else self.loss_good)

