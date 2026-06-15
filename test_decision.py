"""Small interpretable Bayesian network for room cleaning need."""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product


def normalize(distribution: dict[bool, float]) -> dict[bool, float]:
    total = sum(distribution.values())
    if total == 0:
        return {key: 0.0 for key in distribution}
    return {key: value / total for key, value in distribution.items()}


@dataclass(frozen=True)
class SensorEvidence:
    dirt_sensor: bool
    camera_sensor: bool
    occupancy_sensor: bool


class DirtBayesianNetwork:
    """Network: RoomType -> Dirt <- Occupancy; Dirt -> CleaningNeed."""

    room_dirt_prior = {
        "kitchen": 0.72,
        "bathroom": 0.66,
        "living": 0.48,
        "bedroom": 0.35,
        "dining": 0.58,
        "hall": 0.42,
        "general": 0.40,
    }
    sensor_accuracy = {
        "dirt_sensor": (0.90, 0.12),
        "camera_sensor": (0.82, 0.18),
    }

    def bayes_rule(
        self, prior: float, likelihood: float, false_positive: float
    ) -> float:
        evidence = likelihood * prior + false_positive * (1.0 - prior)
        return likelihood * prior / evidence if evidence else 0.0

    def dirt_probability(self, room_type: str, occupied: bool) -> float:
        base = self.room_dirt_prior.get(room_type, self.room_dirt_prior["general"])
        return min(0.98, base + (0.16 if occupied else -0.04))

    def cleaning_need_probability(self, dirt_probability: float, priority: int) -> float:
        need_given_dirt = min(0.99, 0.72 + priority * 0.05)
        need_without_dirt = min(0.35, 0.04 + priority * 0.03)
        return (
            need_given_dirt * dirt_probability
            + need_without_dirt * (1.0 - dirt_probability)
        )

    def fuse_sensors(
        self,
        prior: float,
        evidence: SensorEvidence,
    ) -> tuple[float, list[str]]:
        posterior = prior
        trace = [f"Prior dirt probability was {prior:.1%}."]
        for sensor_name in ("dirt_sensor", "camera_sensor"):
            reading = getattr(evidence, sensor_name)
            true_positive, false_positive = self.sensor_accuracy[sensor_name]
            if reading:
                posterior = self.bayes_rule(posterior, true_positive, false_positive)
            else:
                posterior = self.bayes_rule(
                    posterior, 1.0 - true_positive, 1.0 - false_positive
                )
            trace.append(
                f"{sensor_name.replace('_', ' ').title()}={reading} updated belief "
                f"to {posterior:.1%}."
            )
        occupancy_factor = 1.12 if evidence.occupancy_sensor else 0.94
        posterior = min(0.99, max(0.01, posterior * occupancy_factor))
        trace.append(
            f"Occupancy evidence adjusted the fused dirt probability to {posterior:.1%}."
        )
        return posterior, trace

    def variable_elimination(
        self,
        room_type: str,
        occupancy_probability: float,
        priority: int,
    ) -> dict[bool, float]:
        """Sum out hidden occupancy and dirt variables."""
        distribution = {True: 0.0, False: 0.0}
        for occupied, dirt, need in product((False, True), repeat=3):
            p_occupancy = (
                occupancy_probability if occupied else 1.0 - occupancy_probability
            )
            p_dirt_true = self.dirt_probability(room_type, occupied)
            p_dirt = p_dirt_true if dirt else 1.0 - p_dirt_true
            need_true = self.cleaning_need_probability(float(dirt), priority)
            p_need = need_true if need else 1.0 - need_true
            distribution[need] += p_occupancy * p_dirt * p_need
        return normalize(distribution)

    def predict_markov(self, current_probability: float, steps: int = 1) -> float:
        """Two-state dirt Markov chain: clean->dirty=.18, dirty->dirty=.82."""
        probability = current_probability
        for _ in range(steps):
            probability = probability * 0.82 + (1.0 - probability) * 0.18
        return probability

    def hidden_dirt_filter(
        self, prior: float, sensor_readings: list[bool]
    ) -> list[float]:
        """HMM filtering intuition: transition then incorporate observations."""
        beliefs: list[float] = []
        current = prior
        for reading in sensor_readings:
            predicted = self.predict_markov(current)
            current = self.bayes_rule(
                predicted,
                0.90 if reading else 0.10,
                0.12 if reading else 0.88,
            )
            beliefs.append(current)
        return beliefs

    def rejection_sampling(
        self,
        room_type: str,
        occupied: bool,
        samples: int = 2000,
        seed: int = 42,
    ) -> float:
        rng = random.Random(seed)
        accepted = 0
        needs_cleaning = 0
        for _ in range(samples):
            sampled_occupied = rng.random() < 0.5
            if sampled_occupied != occupied:
                continue
            accepted += 1
            dirt = rng.random() < self.dirt_probability(room_type, sampled_occupied)
            need_probability = self.cleaning_need_probability(float(dirt), 3)
            needs_cleaning += int(rng.random() < need_probability)
        return needs_cleaning / accepted if accepted else 0.0

    def likelihood_weighting(
        self,
        room_type: str,
        occupied: bool,
        samples: int = 2000,
        seed: int = 42,
    ) -> float:
        rng = random.Random(seed)
        weighted_true = 0.0
        total_weight = 0.0
        occupancy_weight = 0.5
        for _ in range(samples):
            dirt = rng.random() < self.dirt_probability(room_type, occupied)
            need_probability = self.cleaning_need_probability(float(dirt), 3)
            need = rng.random() < need_probability
            total_weight += occupancy_weight
            weighted_true += occupancy_weight * int(need)
        return weighted_true / total_weight if total_weight else 0.0
