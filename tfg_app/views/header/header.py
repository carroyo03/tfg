import reflex as rx
from tfg_app.styles.colors import TextColor as txcolor
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.input_text import input_text, AgeState, StartAgeState
from tfg_app.components.date_input_text import date_picker, DateState
from tfg_app.components.gender import gender, GenderState
from tfg_app.components.children import children, RadioGroupState, ChildrenNumberState
from tfg_app.styles.styles import BASE_STYLE
from tfg_app.API.main import calcular_pension
import pandas as pd
import datetime
import logging
from tfg_app.global_state import GlobalState

# Configurar el logging
logging.basicConfig(level=logging.INFO)

class FormState(rx.State):
    form_data: dict = {}

    @rx.event
    async def handle_submit(self, form_data: dict):
        self.save_form_data(form_data)
        self.reset_fields()
        await self.send_data_to_backend(form_data)
        logging.info("Formulario enviado: %s", form_data)
        return rx.redirect("/result")

    def save_form_data(self, form_data: dict):
        # Construir el campo 'date' a partir de 'day', 'month', y 'year'
        form_data['date'] = f"{form_data['day']}/{form_data['month']}/{form_data['year']}"
        # Eliminar los campos 'day', 'month', y 'year' del form_data
        del form_data['day']
        del form_data['month']
        del form_data['year']
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

    async def send_data_to_backend(self, form_data: dict):
        """
        class FormData(BaseModel):
        date: str
        gender: str
        tiene_hijos: str
        n_hijos: str
        edad_jubilacion: str
        salario_actual: float  # Asegúrate de incluir otros campos necesarios
        edad_inicio_trabajo: float  # Por ejemplo, la edad al comenzar a trabajar
        edad_jubilacion_deseada: float  # La edad
        """
        try:
            # Cargar el DataFrame desde el archivo CSV
            df_users = pd.read_csv('usuarios.csv', encoding='unicode_escape', sep=';')
            df_users['fecha_nacimiento'] = pd.to_datetime(df_users['fecha_nacimiento'], format='%d-%m-%Y')
            logging.info("DataFrame cargado: %s", df_users)

            # Verificar los valores de form_data
            logging.info("Valores de form_data: %s", form_data)

            # Filtrar el DataFrame
            df = df_users[
                (df_users['fecha_nacimiento'] == datetime.datetime.strptime(form_data['date'], "%d/%m/%Y")) &
                (df_users['genero'] == form_data['gender']) &
                (
                    (df_users['tiene_hijos'] == 'No') |
                    (df_users['n_hijos'] == int(form_data['n_hijos'])) |
                    ((df_users['n_hijos'] >= 4) & (form_data['n_hijos'] == '4+'))
                ) &
                (df_users['edad_jubilacion_deseada'] == int(form_data['edad_jubilacion']))
            ]

            # Verificar el DataFrame filtrado
            logging.info("DataFrame filtrado: %s", df)

            # Construir form_data a partir del DataFrame filtrado
            if not df.empty:
                form_data = df.iloc[0].to_dict()
            else:
                logging.error("No se encontraron registros que coincidan con los criterios.")
                return

            logging.info("Datos filtrados: %s", form_data)
            pension_primer_pilar = await calcular_pension(form_data)
            logging.info("Pensión primer pilar calculada: %s", pension_primer_pilar)
            
            GlobalState.set_pension_primer_pilar(pension_primer_pilar)
        except Exception as e:
            logging.error("Error al enviar datos al backend: %s", e)


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
