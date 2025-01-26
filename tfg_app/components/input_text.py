import reflex as rx
from tfg_app.styles.fonts import Font

class AgeState(rx.State):
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo edad")
        self.value = ""

class StartAgeState(rx.State):
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    @rx.event
    async def reset_values(self):
        print("Restableciendo edad")
        self.value = ""

class AvgSalaryState(rx.State):
    value = ""

    def set_value(self, value):
        print(f"Estableciendo salario medio: {value}")
        self.value = str(value)
        
    @rx.event
    async def reset_values(self):
        print("Restableciendo salario medio")
        self.set_value("")

def input_text(title: str, name:str, state:rx.State, type_: str) -> rx.Component:
    return rx.vstack(
        rx.text(
            title,
            color="white",
            margin_bottom="0.5em"
        ),
        rx.input(
            type=type_,
            on_change=state.set_value,
            name=name,
            width="100%",
            size="2",
            border_radius="md",
        ),
        font_family=Font.DEFAULT.value,
        width="100%",
        align_items="flex-start"
    )