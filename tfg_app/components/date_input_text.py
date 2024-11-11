import reflex as rx

class Day(rx.State):
    values: list[str] = [str(i) for i in range(1, 32)]
    value: str = "1"
    
    def set_value(self, value: int):
        print(f"Estableciendo día: {value}")
        self.value = value

    def reset_state(self):
        print("Restableciendo día")
        self.value = "1"

class Month(rx.State):
    values: list[str] = [str(i) for i in range(1, 13)]
    value: str = "1"
    
    def set_value(self, value: int):
        print(f"Estableciendo mes: {value}")
        self.value = value

    def reset_state(self):
        print("Restableciendo mes")
        self.value = "1"

class Year(rx.State):
    values: list[str] = [str(i) for i in range(1900, 2024)]
    value: str = "2000"
    
    def set_value(self, value: int):
        print(f"Estableciendo año: {value}")
        self.value = value

    def reset_state(self):
        print("Restableciendo año")
        self.value = "2000"

def date_picker(text: str) -> rx.Component:
    return rx.vstack(
        rx.text(text, color="white", margin_bottom="0.5em"),
        rx.hstack(
            rx.select(
                Day.values,
                placeholder="Día",
                on_change=Day.set_value,
                name="day",
                width="29%",
                color="black"
            ),
            rx.select(
                Month.values,
                placeholder="Mes",
                on_change=Month.set_value,
                name="month",
                width="29%",
                color="black"
            ),
            rx.select(
                Year.values,
                placeholder="Año",
                on_change=Year.set_value,
                name="year",
                width="29%",
                color="black"
            ),
            spacing="5",
            width="100%"
        ),
        width="100%",
        align_items="flex-start"
    )