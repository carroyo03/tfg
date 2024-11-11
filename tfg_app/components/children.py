import reflex as rx
from ..styles.styles import Size as size

class RadioGroupState(rx.State):
    item: str = "None"
    
    def set_item(self, item: str):
        print(f"Estableciendo item: {item}")
        self.item = item
    
    def reset_state(self):
        print("Restableciendo item")
        self.item = "None"

class ChildrenNumberState(rx.State):
    value: str = ""
    
    def set_value(self, value: str):
        print(f"Estableciendo número de hijos: {value}")
        self.value = value
    
    def reset_state(self):
        print("Restableciendo número de hijos")
        self.value = ""

def children() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Tiene hijos?", margin_bottom="0.5em"),
            rx.radio(
                ["Sí", "No"], 
                value=RadioGroupState.item, 
                on_change=RadioGroupState.set_item,
                direction="row", 
                name="tiene_hijos",
                margin_left="2em"
            ),
            width="100%",
            justify="space-between",
            align="center"
        ),
        rx.cond(
            RadioGroupState.item == "Sí",
            rx.vstack(
                rx.text("Cuántos hijos tienes?", margin_bottom="0.5em"),
                rx.select(
                    ["1", "2", "3", "4+"],
                    placeholder="Número de hijos",
                    value=ChildrenNumberState.value,
                    on_change=ChildrenNumberState.set_value,
                    name="n_hijos",
                    width="100%"
                ),
                width="100%",
                align_items="flex-start"
            ),
        ),
        color="white",
        width="100%"
    )