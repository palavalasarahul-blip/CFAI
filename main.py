from probabilistic import DirtBayesianNetwork, SensorEvidence


def test_positive_sensors_raise_probability() -> None:
    network = DirtBayesianNetwork()
    posterior, trace = network.fuse_sensors(
        0.4, SensorEvidence(True, True, False)
    )
    assert posterior > 0.4
    assert len(trace) == 4


def test_variable_elimination_normalizes_distribution() -> None:
    network = DirtBayesianNetwork()
    distribution = network.variable_elimination("kitchen", 0.6, 5)
    assert abs(sum(distribution.values()) - 1.0) < 1e-9
    assert distribution[True] > distribution[False]


def test_markov_prediction_stays_bounded() -> None:
    network = DirtBayesianNetwork()
    prediction = network.predict_markov(0.9, steps=8)
    assert 0.0 <= prediction <= 1.0

