"""Constants for ZSE HDO Live integration.

Author: Miroslav Burdych (@mburdych)
GitHub: https://github.com/mburdych/ZSED-tarify
Support: https://buymeacoffee.com/mburdych

License: MIT
"""

DOMAIN = "zse_hdo"

# Config
CONF_HDO_NUMBER = "hdo_number"
CONF_UPDATE_FREQUENCY = "update_frequency"

# Update frequencies (in seconds)
UPDATE_FREQUENCIES = {
    "5min": {"label": "Každých 5 minút", "seconds": 300, "type": "interval"},
    "1hour": {"label": "Každú hodinu", "seconds": 3600, "type": "interval"},
    "1day": {"label": "1× denne (03:00)", "seconds": 86400, "type": "scheduled"},
    "1week": {"label": "1× týždenne (pondelok 03:00)", "seconds": 604800, "type": "scheduled"},
    "1month": {"label": "1× mesačne (1. deň 03:00)", "seconds": 2592000, "type": "scheduled"}
}

# Scheduled update time (for 1day/1week/1month)
SCHEDULED_UPDATE_HOUR = 3  # 03:00

# Default frequency
DEFAULT_UPDATE_FREQUENCY = "1week"

# Legacy support
UPDATE_INTERVAL = 5  # minutes (deprecated, use CONF_UPDATE_FREQUENCY)
