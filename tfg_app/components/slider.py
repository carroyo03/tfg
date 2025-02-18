import reflex as rx
from tfg_app.styles.styles import Size as size

class SliderState(rx.State):
    value: int = 0

    @rx.event
    def set_end(self,value:list[int]):
        self.value = value[0]



def slider(min_value:int,max_value:int) -> rx.Component:
    return rx.vstack(
        rx.heading(SliderState.value),
        rx.slider(
                default_value=round((min_value+max_value)/2),
                min=min_value,
                max=max_value,
                on_change=SliderState.set_end.throttle(100), # Update the value every 100ms
        ),
        width = "100%"
    )


def rentabilidad_estimada()->rx.Component:
    return rx.vstack(
        rx.heading("Rentabilidad estimada",color="white",font_size=size.BIG.value),
        slider(1,9),
        width="100%",
        padding="1em",
    )