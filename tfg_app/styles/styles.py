import reflex as rx
from enum import Enum
from .colors import Color as color
from .colors import TextColor as txcolor
from .fonts import Font

# Constants
MAX_WIDTH = "37em"

# Sizes
class Size(Enum):
    ZERO = "0px !important"
    SMALL = rx.breakpoints(initial="0.7em", sm="0.85em", md="1em")
    DEFAULT = rx.breakpoints(initial="1em", sm="1.2em", md="1.4em")
    LARGE = rx.breakpoints(initial="1.3em", sm="1.6em", md="1.9em")
    BIG = rx.breakpoints(initial="2em", sm="3em", md="4em")
    REALLY_BIG = rx.breakpoints(initial="3.5em", sm="4.5em", md="5.5em")

# Styles

BASE_STYLE = {
    "background_color" : color.BACKGROUND.value,
    rx.button: {
        "width": "100%",
        "height": "4em",
        "display": "block",
        "padding": Size.DEFAULT.value,
        "border_radius": "md",
        "color": txcolor.HEADER.value,
        "background_color": color.PRIMARY.value,
        "font_weight": "bold",
        "margin_top": "1em",
        "_hover": {
            "background_color": txcolor.HEADER.value,
            "color": color.CONTENT.value,
            "transform": "scale(1.02)",
            "transition": "all 0.2s ease-in-out"
        }
    },
    rx.link:{
        "text_decoration": "none",
        "_hover": {},
    }
}

navbar_title_style = dict(
    font_family = Font.LOGO.value + ", sans-serif",
    font_size = Size.LARGE.value
)

title_style=dict(
    width = "100%",
    font_family = Font.TITLE.value,
    padding_top = Size.DEFAULT.value,
    color = txcolor.HEADER.value
)

button_title_style = dict(
    font_family = Font.DEFAULT.value,
    font_weight = "bold",
    font_size = Size.SMALL.value,
    color=txcolor.HEADER.value

)

button_body_style = dict(
    font_family = Font.DEFAULT.value,
    font_size = Size.SMALL.value,
    color=txcolor.BODY.value
    
)