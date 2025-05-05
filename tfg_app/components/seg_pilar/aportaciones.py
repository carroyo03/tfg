

import reflex as rx
from tfg_app.styles.styles import Size as size

class Company2PState(rx.State):
    value : float = 0

    def set_value(self,value):
        self.value = float(value) if value != '' else 0

    @rx.event
    async def reset_values(self):
        self.value = 0

    @rx.var
    def empty_value(self) -> bool:
        return self.value is None
    
    @rx.var
    def invalid_value(self) -> bool:
        if not self.empty_value:
            v = int(self.value)
            return v < 0 or v > 20
        return False



class Employee2PState(rx.State):
    value: str = "None"
    
    def set_value(self, value: str):
        print(f"Estableciendo value: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo value")
        self.value = "None"



def aportar(text:str) -> rx.Component:
    return rx.vstack(
        rx.stack(
            rx.text(text),
            rx.radio(
                ["Sí", "No"], 
                value=Employee2PState.value, 
                on_change=Employee2PState.set_value,
                direction=rx.breakpoints(initial='row', sm= 'column'), 
                name="quiere_aportar",
                margin_left="2em"
            ),
            width="100%",
            justify="between",
            align="center"
        ),
        color="white",
        width="100%"
    )