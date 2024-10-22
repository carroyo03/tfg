import reflex as rx
import reflex_chakra as rc
from ..styles.styles import Size as size


def navbar()->rx.Component:
    return rx.hstack(
        rx.box(
            rc.image(src="/icons/KPMG_NoCP_White.png",
                     height=size.BIG.value,
                     width=size.REALLY_BIG.value,
                     margin_left = size.DEFAULT.value,
                     margin_top = size.DEFAULT.value)
        )
    )