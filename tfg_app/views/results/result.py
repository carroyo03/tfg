import reflex as rx
from tfg_app.global_state import GlobalState
from tfg_app.styles.fonts import Font
from tfg_app.styles.styles import Size as size

class ResultState(rx.State):
    @rx.var
    def formatted_pension(self) -> str:
        return f"{GlobalState.pension_primer_pilar:.2f}€"

def final_result() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Resultados",
            color="white",
            font_family=Font.TITLE.value,
            font_size=size.BIG.value,
            font_weight="bold",
            margin_top=size.SMALL.value,
        ),
        rx.text(
            f"La pensión mensual estimada es: {ResultState.formatted_pension}",
            color="white"
        )
    )