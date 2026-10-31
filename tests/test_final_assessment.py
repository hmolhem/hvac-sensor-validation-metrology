import numpy as np

from src.final_assessment import pooled_sigma_upper_confidence_limit


def test_repeatability_common_sigma_ucl_matches_frozen_evidence():
    pooled_sd = 0.2592654906322251
    degrees_of_freedom = 120 * (60 - 1)

    ucl = pooled_sigma_upper_confidence_limit(
        pooled_sd,
        degrees_of_freedom,
        confidence=0.95,
    )

    assert np.isclose(ucl, 0.2629034866, rtol=0.0, atol=2e-6)
    assert ucl < 0.30


def test_repeatability_ucl_rejects_invalid_inputs():
    for pooled_sd, df, confidence in [
        (-0.1, 10, 0.95),
        (0.2, 0, 0.95),
        (0.2, 10, 1.0),
    ]:
        try:
            pooled_sigma_upper_confidence_limit(
                pooled_sd,
                df,
                confidence=confidence,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for invalid UCL input")
