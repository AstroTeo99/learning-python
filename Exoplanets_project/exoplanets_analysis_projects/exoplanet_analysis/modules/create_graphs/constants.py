import numpy as np

CONSTANTS = {
    'Earth_mass': {
        'value': 5.9722e24,  # kg
        'uncertainty': 0.0006 * 5.9722e24  # kg
    },
    'Jupiter_mass': {
        'value': 1.89813e27,  # kg
        'uncertainty': 0.00019 * 1.89813e27  # kg
    },
    'Sun_mass': {
        'value': 1.988475e30,  # kg
        'uncertainty': 0.000092 * 1.988475e30  # kg
    },
    'Earth_flux': {
        'value': 1361,  # W/m^2
        'uncertainty': 0
    },
    'Earth_radius': {
        'value': 6371,  # km
        'uncertainty': 0
    },
    'Jupiter_radius': {
        'value': 69911,  # km
        'uncertainty': 0
    },
    'Sun_radius': {
        'value': 696340,  # km
        'uncertainty': 0
    },
    'pi': {
        'value': np.pi,
        'uncertainty': 0
    }
}
