
from types import MappingProxyType

from .setting_heatmap import HEATMAP_DEFAULT_TYRE

COMPOUNDINFO_DEFAULT = MappingProxyType({
    "symbol": "?",
    "heatmap": HEATMAP_DEFAULT_TYRE,
})

COMPOUNDS_DEFAULT = {
    "Hyper - Soft": {
        "symbol": "S",
        "heatmap": "tyre_optimal_70",
    },
    "Hyper - Medium": {
        "symbol": "M",
        "heatmap": "tyre_optimal_80",
    },
    "Hyper - Hard": {
        "symbol": "H",
        "heatmap": "tyre_optimal_90",
    },
    "Hyper - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - Soft": {
        "symbol": "S",
        "heatmap": "tyre_optimal_70",
    },
    "LMP2 - Medium": {
        "symbol": "M",
        "heatmap": "tyre_optimal_80",
    },
    "LMP2 - Hard": {
        "symbol": "H",
        "heatmap": "tyre_optimal_90",
    },
    "LMP2 - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "GTE - Soft": {
        "symbol": "S",
        "heatmap": "tyre_optimal_80",
    },
    "GTE - Medium": {
        "symbol": "M",
        "heatmap": "tyre_optimal_90",
    },
    "GTE - Hard": {
        "symbol": "H",
        "heatmap": "tyre_optimal_100",
    },
    "GTE - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "GTE - P2M (Rain)": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "GT3 - Soft": {
        "symbol": "S",
        "heatmap": "tyre_optimal_80",
    },
    "GT3 - Medium": {
        "symbol": "M",
        "heatmap": "tyre_optimal_90",
    },
    "GT3 - Hard": {
        "symbol": "H",
        "heatmap": "tyre_optimal_100",
    },
    "GT3 - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "GT3 - P2M (Rain)": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "BTCC - Soft": {
        "symbol": "S",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "BTCC - Medium": {
        "symbol": "M",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "BTCC - Hard": {
        "symbol": "H",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "BTCC - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "Hypercar - Soft": {
        "symbol": "S",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "Hypercar - Medium": {
        "symbol": "M",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "Hypercar - Hard": {
        "symbol": "H",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "Hypercar - Wet": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - S7M (Soft)": {
        "symbol": "S",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - S8M (Medium)": {
        "symbol": "M",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - S9M (Hard)": {
        "symbol": "H",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - H5M (Inter)": {
        "symbol": "I",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP2 - P2M (Rain)": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP3 - S8M (Medium)": {
        "symbol": "M",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
    "LMP3 - P2M (Rain)": {
        "symbol": "W",
        "heatmap": HEATMAP_DEFAULT_TYRE,
    },
}
