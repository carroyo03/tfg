import reflex as rx

class GenderState(rx.State):
    values: list[str] = ["Hombre", "Mujer"]
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo género: {value}")
        self.value = value

    @rx.event
    async def reset_values(self):
        print("Restableciendo género")
        self.value = ""

def gender() -> rx.Component:
    return rx.vstack(
        rx.text("Género", color="white"),
        rx.select(GenderState.values, placeholder="Elige:", on_change=GenderState.set_value, name="gender", width="100%"),
        width="100%",
        align_items="flex-start"
    )
        