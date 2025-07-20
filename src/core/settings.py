import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# --- Site Data ---
SITEURL = os.getenv("SITEURL", default="https://zmudzinski.sh")
DESCRIPTION = os.getenv("DESCRIPTION", default="I write Python code. Kinda.")
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
STATIC_PATHS = ["images", "extra/CNAME"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
}

MARKDOWN = {
    'extensions': ['codehilite', 'extra', 'smarty'],
    'extension_configs': {
        'smarty': {
            'smart_quotes': False,
        }
    }
}

# --- Code highlightning ---
# MARKDOWN = {
#     'extension_configs': {
#         'markdown.extensions.codehilite': {
#             'css_class': 'codehilite',
#         },
#     },
# }

# --- Menu ---
MENU = {
    "Posts": "/",
    "About": "/about",
}

# --- Site Data ---
SITE_DATA: dict[str, dict | int] = {
    "year": datetime.now().year,
}
