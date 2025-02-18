import reflex as rx
from tfg_app.styles.styles import Size as size

class SliderState(rx.State):
    min_value:int = 0
    max_value:int = 100
    value:int = round((min_value+max_value)/2)

    def set_rank_values(self,min_:int,max_:int):
        self.min_value = min_
        self.max_value=max_
        self.value = round((min_+max_)/2)

    @rx.event
    def set_end(self,value:list):
        self.value = value[0]

    @rx.event
    async def reset_values(self):
        self.value = 0  


def slider(min_value: int, max_value: int, name:str) -> rx.Component:
    # Trigger the event asynchronously without blocking component rendering.
    return rx.vstack(
        rx.heading(SliderState.value, font_size=size.SMALL.value, color="white"),
        rx.slider(
            default_value=round((min_value + max_value) / 2),
            min=min_value,
            max=max_value,
            on_change=SliderState.set_end.throttle(100),  # Update the value every 100ms
            name=name
        ),
        on_mount=lambda: SliderState.set_rank_values(min_value, max_value),
        width="100%",
    )

def rentabilidad_estimada(num_pilar:int) -> rx.Component:
    return rx.vstack(
        rx.heading("Rentabilidad estimada (%)", color="white", font_size=size.SMALL.value),
        slider(1, 9,f"rentabilidad_{num_pilar}"),
        width="100%",
    )