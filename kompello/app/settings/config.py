import json
from pathlib import Path

_config = {}

def get_secret(key: str, default=None):
    global _config
    if _config == {}:
        with open(Path(__file__).resolve().parent.parent.parent.parent / "settings.json", "r") as file:
            _config = json.load(file)

    var = _config
    for sub in key.split("."):
        if sub in var:
            var = var[sub]
            continue
        return default

    return var
