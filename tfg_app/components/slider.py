import reflex as rx
from tfg_app.components.info_button import info_button
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
    
    @rx.var
    def riesgo_label(self) -> str:
        if self.value <= 2:
            return "Conservador"
        elif self.value <= 5:
            return "Moderado"
        elif self.value < 8:
            return "Alto"
        return "Muy alto"


def slider(min_value: int, max_value: int, name: str) -> rx.Component:
    return rx.vstack(
        rx.heading(
            SliderState.riesgo_label,
            font_size='1rem',
            color="white"
        ),
        rx.slider(
            default_value=round((min_value + max_value) / 2),
            min=min_value,
            max=max_value,
            on_change=SliderState.set_end.throttle(100),
            name=name
        ),
        on_mount=lambda: SliderState.set_rank_values(min_value, max_value),
        width="100%",
    )

def tipo_riesgo_pension(num_pilar: int) -> rx.Component:
    info_content = (
        "- Conservador: Inversión muy segura, con poco riesgo de perder dinero, pero con ganancias pequeñas. Ideal si prefieres estabilidad.\n\n"
        "- Moderado: Equilibrio entre seguridad y crecimiento, con riesgo medio. Puedes ganar más, pero hay posibilidad de pequeñas pérdidas.\n\n"
        "- Alto: Mayor riesgo, con posibilidad de ganar mucho o perder parte. Adecuado si aceptas incertidumbre por mejores retornos.\n\n"
        "- Muy alto: Riesgo elevado, con grandes oportunidades de ganancia, pero también de perder mucho. Solo para quienes aceptan variabilidad.\n\n\n"
        "Consulta con un asesor financiero antes de tomar una decisión."
    )
    return rx.vstack(
        rx.hstack(
            rx.heading("Riesgo de la inversión", color="white", font_size='1rem'),
            info_button(info=info_content, color="white"),
            align='center'
        ),
        slider(1, 9, f"rentabilidad_{num_pilar}"),
        width="100%",
    )