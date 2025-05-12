import reflex as rx

class Employee3PState(rx.State):
    value: str = "None"
    
    def set_value(self, value: str):
        print(f"Estableciendo value: {value}")
        self.value = value

    @rx.var
    def empty_value(self) -> bool:
        return self.value is None or self.value == "None"

    @rx.var
    def invalid_value(self) -> bool:
        if not self.empty_value:
            v = int(self.value)
            return v < 0
        return False
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo value")
        self.value = "None"