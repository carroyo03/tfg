import reflex as rx

class GenderState(rx.State):
    values: list[str] = ["Hombre", "Mujer"]
    value: str = "Hombre"
    
    def set_value(self, value: str):
        print(f"Estableciendo género: {value}")
        self.value = value

    def reset_state(self):
        print("Restableciendo género")
        self.value = "Hombre"

def gender() -> rx.Component:
    return rx.vstack(
        rx.text("Género", color="white"),
        rx.select(GenderState.values, placeholder="Elige:", on_change=GenderState.set_value, name="gender", width="100%"),
        width="100%",
        align_items="flex-start"
    )
        