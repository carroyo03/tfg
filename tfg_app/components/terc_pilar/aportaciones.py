import reflex as rx

class Employee3PState(rx.State):
    value: str = "None"
    
    def set_value(self, value: str):
        print(f"Estableciendo value: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo value")
        self.value = "None"