import reflex as rx
import reflex_chakra as rc
from tfg_app.styles.styles import Size as size




def navbar()->rx.Component:
    return rx.hstack(
        rx.box(
            rc.image(
                src="/icons/KPMG_NoCP_White.png",
                alt="Logo de KPMG",
                loading="lazy",
                height=["8vw", "6vw", "4vw"],  # Increased size for mobile
                width="auto",
                margin_left=["0.5em", size.DEFAULT.value, size.DEFAULT.value],
                margin_top=["0.5em", size.DEFAULT.value, size.DEFAULT.value]
            )
        ),
        width="100%",
        padding="1em",
        position="absolute",
        top="0",
        z_index="1000",
        align="center"
    )