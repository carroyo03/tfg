import reflex as rx
from tfg_app.styles.colors import TextColor as txcolor
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.input_text import input_text, AgeState, StartAgeState
from tfg_app.components.date_input_text import date_picker, DateState
from tfg_app.components.gender import gender, GenderState
from tfg_app.components.children import children, RadioGroupState, ChildrenNumberState
from tfg_app.styles.styles import BASE_STYLE




class FormState(rx.State):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        print("Formulario enviado:", form_data)
        self.save_form_data(form_data)
        self.reset_fields()

    def save_form_data(self, form_data: dict):
        # Función separada para manejar el guardado de datos
        self.form_data = form_data

    def reset_fields(self):
        # Restablece los campos, reutilizando la función
        for field in self.default_fields():
            field.reset_state()

    def default_fields(self):
        yield DateState
        yield GenderState
        yield RadioGroupState
        yield ChildrenNumberState
        yield StartAgeState
        yield AgeState

def form_example():
    return rx.form(
        rx.vstack(
            date_picker("Fecha de nacimiento"),
            gender(),
            children(),
            input_text("Edad a la que empezaste a cotizar", StartAgeState, "number"),
            input_text("Edad deseada de jubilación", AgeState, "number"),
            rx.button("Siguiente", type="submit"),
            width="100%",
            spacing="5",
            padding=["1em", "1.5em", "2em"],
            max_width="100%",
            font_weight='bold'
        ),
        overflow="hidden",
        on_submit=FormState.handle_submit,
        reset_on_submit=True,
        margin_top=size.DEFAULT.value,
    )
def header():
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "Simulador de pensiones",
                color = "white",
                font_family = Font.TITLE.value,
                font_size = size.BIG.value,
                font_weight = "bold",
                margin_top = size.SMALL.value,
            ),
            form_example(),
            overflow = "hidden",
            align="center",
            padding="1em",
            height="100%",
        ),
    )
