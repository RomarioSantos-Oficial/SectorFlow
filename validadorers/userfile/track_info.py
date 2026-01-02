
from __future__ import annotations

from ..const_file import ConfigType
from ..setting import cfg
from ..template.setting_tracks import TRACKINFO_DEFAULT
from ..validator import invalid_save_name


def add_missing_track(track_name: str) -> dict:
    """Add missing track info to tracks preset"""
    new_data = TRACKINFO_DEFAULT.copy()
    cfg.user.tracks[track_name] = new_data
    return new_data


def load_track_info(track_name: str) -> dict:
    """Load track info from tracks preset"""
    return cfg.user.tracks.get(track_name, TRACKINFO_DEFAULT)


def save_track_info(track_name: str, **track_info: dict) -> None:
    """Save track info to tracks preset"""
    if invalid_save_name(track_name):
        return
    track = cfg.user.tracks.get(track_name)
    if not isinstance(track, dict):
        track = add_missing_track(track_name)
    track.update(track_info)
    cfg.save(cfg_type=ConfigType.TRACKS)
