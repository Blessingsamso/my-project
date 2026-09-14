"""
Nigerian States and Local Government Areas (LGAs) Data Module.
Restricted to Adamawa State and its specified Local Government Areas.
"""

NIGERIA_STATES_AND_LGAS = {
    "Adamawa": [
        "Gombi",
        "Guyuk",
        "Hong",
        "Madagali",
        "Maiha",
        "Michika",
        "Mubi North",
        "Mubi South"
    ]
}


def get_nigerian_states():
    """Return a sorted list of all Nigerian States (Adamawa only)."""
    return sorted(list(NIGERIA_STATES_AND_LGAS.keys()))


def get_state_choices():
    """Return tuple of choices for Django Form fields."""
    return [(state, state) for state in get_nigerian_states()]


def get_lgas_for_state(state_name):
    """Return sorted list of LGAs for a given state."""
    if not state_name:
        state_name = "Adamawa"
    return sorted(NIGERIA_STATES_AND_LGAS.get(state_name, NIGERIA_STATES_AND_LGAS["Adamawa"]))
