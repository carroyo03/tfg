import reflex as rx
import reflex_chakra as rc
from ..styles.styles import Size as size


def navbar()->rx.Component:
    return rx.hstack(
        rx.box(
            rc.image(
                src="/icons/KPMG_NoCP_White.png",
                alt = "Logo de KPMG",
                loading="lazy",
                height=["5vw", "4vw", "3vw"],
                width=["7vw", "6vw", "5vw"],
                margin_left=["0.5em", size.DEFAULT.value, size.DEFAULT.value],
                margin_top=["0.5em", size.DEFAULT.value, size.DEFAULT.value]
            )
        ),
        width="100%",
        padding="1em",
        position= "fixed",
        top = "0",
        z_index = "1000"
    )