import reflex as rx
from tfg_app.global_state import GlobalState

def final_result() -> rx.Component:
    return rx.vstack(
        rx.text("Resultados", color="white"),
        rx.text(f"La pensión final es de {GlobalState.get_pension_primer_pilar()}€", color="white"),
    )