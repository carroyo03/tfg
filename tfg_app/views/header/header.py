import reflex as rx
from tfg_app.styles.colors import TextColor as txcolor
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.input_text import input_text, AgeState, StartAgeState
from tfg_app.components.date_input_text import date_picker, DateState
from tfg_app.components.gender import gender, GenderState
from tfg_app.global_state import GlobalState
from tfg_app.components.children import children, RadioGroupState, ChildrenNumberState
from tfg_app.components.tipo_regimen import tipo_regimen, RadioGroup1State, TypeRegState, LagsCotState
from tfg_app.styles.styles import BASE_STYLE
import pandas as pd
import datetime
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO)

class FormState(rx.State):
    form_data: dict = {}

    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            self.save_form_data(form_data)
            pension = await self.send_data_to_backend(form_data)
            # Obtener una instancia del estado global
            state = await self.get_state(GlobalState)
            # Actualizar el valor de pension_primer_pilar
            state.set_pension_primer_pilar(pension)
            return rx.redirect("/pilar1")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    def save_form_data(self, form_data: dict):
        form_data['fecha_nacimiento'] = f"{form_data['day']}/{form_data['month']}/{form_data['year']}"
        del form_data['day']
        del form_data['month']
        del form_data['year']
        self.form_data = form_data

    def reset_fields(self):
        for field in self.default_fields():
            field.reset_state()

    def default_fields(self):
        yield DateState
        yield GenderState
        yield RadioGroupState
        yield ChildrenNumberState
        yield StartAgeState
        yield AgeState
        yield RadioGroup1State
        yield TypeRegState
        yield LagsCotState

    async def send_data_to_backend(self, form_data: dict):
        from tfg_app.API.main import calcular_pension
        try:
            df_users = pd.read_csv('usuarios.csv', encoding='unicode_escape', sep=';')
            df_users['fecha_nacimiento'] = pd.to_datetime(df_users['fecha_nacimiento'], format='%d-%m-%Y')
            logging.info("DataFrame cargado: %s", df_users)

            logging.info("Valores de form_data: %s", form_data)

            df = df_users[
                (df_users['fecha_nacimiento'] == datetime.datetime.strptime(form_data['fecha_nacimiento'], "%d/%m/%Y")) &
                (df_users['genero'] == form_data['gender']) &
                (
                    (df_users['tiene_hijos'] == 'No') |
                    (df_users['n_hijos'] == int(form_data['n_hijos'])) |
                    ((df_users['n_hijos'] >= 4) & (form_data['n_hijos'] == '4+'))
                ) &
                (df_users['edad_jubilacion_deseada'] == int(form_data['edad_jubilacion']))
            ]

            logging.info("DataFrame filtrado: %s", df)

            if not df.empty:
                form_data = df.iloc[0].to_dict()
            else:
                logging.error("No se encontraron registros que coincidan con los criterios.")
                return

            logging.info("Datos filtrados: %s", form_data)
            pension = await calcular_pension(form_data)
            self.form_data = form_data
            logging.info(f"Pensión calculada: {pension}")
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e

def form_example():
    return rx.form(
        rx.vstack(
            date_picker("Fecha de nacimiento"),
            gender(),
            children(),
            input_text("Edad a la que empezaste a cotizar", StartAgeState, "number"),
            input_text("Edad deseada de jubilación", AgeState, "number"),
            tipo_regimen(),
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
                color="white",
                font_family=Font.TITLE.value,
                font_size=size.BIG.value,
                font_weight="bold",
                margin_top=size.SMALL.value,
            ),
            form_example(),
            overflow="hidden",
            align="center",
            padding="1em",
            height="100%",
        ),
    )
