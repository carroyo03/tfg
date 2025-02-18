import reflex as rx
from tfg_app.styles.styles import Size as size



class RadioGroup1State(rx.State):
    item: str = "None"
    
    def set_item(self, item: str):
        print(f"Estableciendo item: {item}")
        self.item = item
    @rx.event
    async def reset_values(self):
        print("Restableciendo item")
        self.item = "None"

class TypeRegState(rx.State):
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo número de hijos: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo número de hijos")
        self.value = ""

class LagsCotState(rx.State):
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo número de hijos: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo número de hijos")
        self.value = ""

def tipo_regimen() -> rx.Component:
    return rx.vstack(
             rx.vstack(
                rx.text("Régimen de cotización", margin_bottom="0.5em"),
                rx.select(
                    ["General", "Autónomo"],
                    placeholder="Selecciona",
                    value=TypeRegState.value,
                    on_change=TypeRegState.set_value,
                    name="r_cotizacion",
                    width="100%"
                ),
                width="100%",
                align_items="flex-start"
                ),

        rx.hstack(
            rx.text("¿Existen lagunas de cotización?"),
            rx.radio(
                ["Sí", "No"], 
                value=RadioGroup1State.item, 
                on_change=RadioGroup1State.set_item,
                direction="row", 
                name="lagunas_cotizacion",
                margin_left="2em"
            ),
            width="100%",
            justify="between",
            align="center"
        ),
        rx.cond(
            RadioGroup1State.item == "Sí",
                rx.vstack(
                    rx.text("¿Cuántos años de lagunas de cotización tienes?", color="white"),
                    rx.input(
                        placeholder="",
                        type="number",
                        on_change=LagsCotState.set_value,
                        name="n_lagunas",
                        width="100%",
                        size="2",
                        border_radius="md",
                    ),
                    width="100%",
                ),
        ),
        color="white",
        width="100%"
    )