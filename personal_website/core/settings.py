import os
from datetime import datetime

from dotenv import load_dotenv

from personal_website.animal.repository import animal_repository
from personal_website.event.repository import event_repository
from personal_website.person.repository import person_repository

load_dotenv()

# --- Site Data ---
SITEURL = os.getenv("SITEURL", default="https://zmudzinski.me")
DESCRIPTION = os.getenv("DESCRIPTION", default="I write Python code and do nerdy things.")
AUTHOR = "Lukasz Zmudzinski"
SITENAME = "zmudzinski.me"
TIMEZONE = "Europe/Warsaw"
DEFAULT_LANG = "en"

SITE_DATA: dict[str, object] = {
    "year": datetime.now().year,
    "family": {
        "people": person_repository.get_items(),
        "animals": animal_repository.get_items(),
        "events": event_repository.get_items(),
    },
    "repository": {
        "pelican": "https://getpelican.com/",
        "link": "https://github.com/lukzmu/personal-website",
    },
}

# --- Feed Settings ---
FEED_ALL_ATOM = "feed.xml"
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# --- Pelican Paths and Settings ---
PATH = "personal_website/content"
THEME = "personal_website/themes/core"
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
ARTICLE_URL = "posts/{slug}.html"
ARTICLE_SAVE_AS = "posts/{slug}.html"

MARKDOWN = {
    "extensions": ["codehilite", "extra", "smarty"],
    "extension_configs": {
        "smarty": {
            "smart_quotes": False,
        }
    },
}
