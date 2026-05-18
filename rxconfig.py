import reflex as rx
from dotenv import load_dotenv
import os
load_dotenv()

config = rx.Config(
    app_name=os.getenv("REFLEX_APP_NAME", "tfg_app"),
    show_built_with_reflex=False,
    disable_plugins=["SitemapPlugin"]
)