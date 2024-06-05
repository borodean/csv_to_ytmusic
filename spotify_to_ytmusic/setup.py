import json
import shutil
import sys
from pathlib import Path
from typing import Optional

import ytmusicapi

from spotify_to_ytmusic.settings import DEFAULT_PATH, EXAMPLE_PATH, Settings
from spotify_to_ytmusic.utils.browser import has_browser


def setup(file: Optional[Path] = None):
    if file:
        shutil.copy(file, DEFAULT_PATH)
        return

    if not DEFAULT_PATH.is_file():
        shutil.copy(EXAMPLE_PATH, DEFAULT_PATH)

    setup_youtube()


def setup_youtube():
    settings = Settings()
    credentials = ytmusicapi.setup_oauth(open_browser=has_browser())
    settings["youtube"]["headers"] = json.dumps(credentials.as_dict())
    settings.save()
