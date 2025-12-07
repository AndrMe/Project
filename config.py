import os
from pathlib import Path
import configparser
import sys

from typing import Any


def getConfigPath(filename:str="settings.conf") -> Path:

    home = Path.home()
    if os.name == "nt":  # Windows
        base = Path(os.getenv("APPDATA", home / "AppData" / "Roaming")) / "MyEditor"
    elif sys.platform == "darwin":  # macOS
        base = home / "Library" / "Application Support" / "MyEditor"
    else:  # Linux, Unix
        base = home / ".config" / "MyEditor"
    
    base.mkdir(parents=True, exist_ok=True)
    return base / filename

CONFIG_PATH = getConfigPath("settings.conf")

def saveSettings(encrypt: bool, autosave: bool, autosave_interval: float):
    print("Saving Config")
    config = configparser.ConfigParser()
    config['General'] = {
        'encrypt': str(encrypt),
        'autosave': str(autosave),
        'autosave_interval': str(autosave_interval)
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)
        print("Saved Config")

def ifNull(value: Any, displayWhenNone:Any):
    return value if value is not None else displayWhenNone



DEFAULT_CONFIG = (False, True, 5.0)

def loadSettings():
    config = configparser.ConfigParser()
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG
    config.read(CONFIG_PATH, encoding="utf-8")
    g = config['General']
    return (g.getboolean('encrypt', fallback=DEFAULT_CONFIG[0]),
            g.getboolean('autosave', fallback=DEFAULT_CONFIG[1]),
            g.getfloat('autosave_interval', fallback=DEFAULT_CONFIG[2]))

