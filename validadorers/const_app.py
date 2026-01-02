

import platform

from . import version_check
from .i18n import i18n, _
from .userfile import set_global_user_path

# System info
PLATFORM = platform.system()

# App version
VERSION = version_check.tinypedal()

# App info
APP_NAME = "SectorFlow"
REPO_NAME = "SectorFlow/SectorFlow"
COPYRIGHT = "Copyright (C) 2022-2025 SectorFlow developers"
DESCRIPTION = (
    "Free and Open Source telemetry overlay application "
    "for racing simulation."
)
LICENSE = "Licensed under the GNU General Public License v3.0 or later."

# URL
URL_WEBSITE = f"https://github.com/{REPO_NAME}"
URL_USER_GUIDE = f"{URL_WEBSITE}/wiki/User-Guide"
URL_FAQ = f"{URL_WEBSITE}/wiki/FAQ"
URL_RELEASE = f"{URL_WEBSITE}/releases"

# Global path
PATH_GLOBAL = set_global_user_path(APP_NAME, PLATFORM)
