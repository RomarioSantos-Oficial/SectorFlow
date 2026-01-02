
from types import MappingProxyType

from .setting_heatmap import HEATMAP_DEFAULT_BRAKE

BRAKEINFO_DEFAULT = MappingProxyType({
    "failure_thickness": 0.0,
    "heatmap": HEATMAP_DEFAULT_BRAKE,
})

BRAKES_DEFAULT = {
    "Hyper - Front Brake": {
        "failure_thickness": 25.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "Hyper - Rear Brake": {
        "failure_thickness": 25.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "LMP2 - Front Brake": {
        "failure_thickness": 25.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "LMP2 - Rear Brake": {
        "failure_thickness": 25.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "GTE - Front Brake": {
        "failure_thickness": 30.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "GTE - Rear Brake": {
        "failure_thickness": 30.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "GT3 - Front Brake": {
        "failure_thickness": 30.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
    "GT3 - Rear Brake": {
        "failure_thickness": 30.0,
        "heatmap": HEATMAP_DEFAULT_BRAKE,
    },
}
