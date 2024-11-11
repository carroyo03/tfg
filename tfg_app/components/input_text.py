import reflex as rx
from tfg_app.styles.fonts import Font

class AgeState(rx.State):
    value: str = "65"
    
    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    
    def reset_state(self):
        print("Restableciendo edad")
        self.value = "65"

class StartAgeState(rx.State):
    value: str = "24"
    
    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    
    def reset_state(self):
        print("Restableciendo edad")
        self.value = "24"

def input_text(title: str, state:rx.State, type: str) -> rx.Component:
    return rx.vstack(
        rx.text(
            title,
            color="white",
            margin_bottom="0.5em"
        ),
        rx.input(
            placeholder=state.value,
            type=type,
            on_change=state.set_value,
            name="edad_jubilacion",
            width="100%",
            size="lg",
            border_radius="md",
        ),
        font_family=Font.DEFAULT.value,
        width="100%",
        align_items="flex-start"
    )