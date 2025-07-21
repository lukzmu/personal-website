import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# --- Site Data ---
SITEURL = os.getenv("SITEURL", default="https://zmudzinski.sh")
DESCRIPTION = os.getenv("DESCRIPTION", default="I write Python code and do nerdy things.")
AUTHOR = "Lukasz Zmudzinski"
SITENAME = "zmudzinski.sh"
TIMEZONE = "Europe/Warsaw"
DEFAULT_LANG = "en"

# --- Pelican Paths and Settings ---
PATH = "src/content"
THEME = "src/themes/core"
THEME_STATIC_DIR = "theme"
DEFAULT_PAGINATION = False
DELETE_OUTPUT_DIRECTORY = True
STATIC_PATHS = ["images", "extra"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/android-chrome-192x192.png": {"path": "android-chrome-192x192.png"},
    "extra/android-chrome-512x512.png": {"path": "android-chrome-512x512.png"},
    "extra/apple-touch-icon.png": {"path": "apple-touch-icon.png"},
    "extra/favicon-16x16.png": {"path": "favicon-16x16.png"},
    "extra/favicon-32x32.png": {"path": "favicon-32x32.png"},
    "extra/favicon.ico": {"path": "favicon.ico"},
    "extra/site.webmanifest": {"path": "site.webmanifest"},
}

MARKDOWN = {
    'extensions': ['codehilite', 'extra', 'smarty'],
    'extension_configs': {
        'smarty': {
            'smart_quotes': False,
        }
    }
}

# --- Menu ---
MENU = {
    "Posts": "/",
    "About": "/about",
}

# --- Site Data ---
SITE_DATA: dict[str, dict | int] = {
    "year": datetime.now().year,
}
