import reflex as rx
from enum import Enum
from .colors import Color as color
from .colors import TextColor as txcolor
from .fonts import Font

# Constants
MAX_WIDTH = "600px"

# Sizes
class Size(Enum):
    ZERO = "0px !important"
    SMALL = "0.85em"
    DEFAULT = "1.2em"
    LARGE = "1.6em"
    BIG = "3em"
    REALLY_BIG = "4em"

# Styles

BASE_STYLE = {
    "background_color" : color.BACKGROUND.value,
    rx.button:{
        "width":"100%",
        "height":"100%",
        "display":"block",
        "padding": Size.SMALL.value,
        "border_radius":Size.DEFAULT.value,
        "color": txcolor.HEADER.value,
        "background_color" : color.CONTENT.value,
        "_hover":{
            "background_color" : color.SECONDARY.value
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
    font_family = Font.TITLE.value,
    font_weight = "bold",
    font_size = Size.DEFAULT.value,
    color=txcolor.HEADER.value

)

button_body_style = dict(
    font_family = Font.DEFAULT.value,
    font_size = Size.SMALL.value,
    color=txcolor.BODY.value
    
)