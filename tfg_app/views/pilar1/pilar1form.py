import reflex as rx
from tfg_app.styles.colors import TextColor as txcolor, Color as color
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.input_text import input_text, AgeState, StartAgeState, AvgSalaryState
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
    is_loading: bool = False
    
    @rx.var
    def stored_form_data(self) -> dict:
        """Una computed var que maneja los datos del formulario."""
        return self.form_data

    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            form_data['fecha_nacimiento'] = f"{form_data['day']}/{form_data['month']}/{form_data['year']}"
            del form_data['day']
            del form_data['month']
            del form_data['year']
            self.form_data = form_data
            
            pension = await self.send_data_to_backend(self.form_data)
            state = await self.get_state(GlobalState)
            state.set_pension("primer",pension)
            return rx.redirect("/pilar1")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    @rx.event
    async def clear_form(self):

        self.is_loading = True

        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [AgeState, GenderState, DateState, RadioGroupState, 
                            ChildrenNumberState, StartAgeState, 
                            RadioGroup1State, TypeRegState,
                            LagsCotState, AvgSalaryState]:
            state= await self.get_state(state_class)
            await state.reset_values()
        
        # Fuerza actualización del frontend
        return rx.call_script("window.location.reload();")
    
        # Obtén y resetea cada estado individual
        """for state_class in self.default_fields():
            state = await self.get_state(state_class)
            await state.reset_values()
        
        return rx.call_script("window.location.reload();")
        """

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
        yield AvgSalaryState

    async def send_data_to_backend(self, form_data: dict):
        from tfg_app.backend.main import calcular_pension_1p
        try:
            """
            df_users = pd.read_csv('usuarios.csv', encoding='unicode_escape', sep=';')
            df_users['fecha_nacimiento'] = pd.to_datetime(df_users['fecha_nacimiento'], format='%d-%m-%Y')
            logging.info("DataFrame cargado: %s", df_users)
 """
            logging.info("Valores de form_data: %s", form_data)

            """
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
            """

            df= pd.DataFrame()
            df["fecha_nacimiento"] = [datetime.datetime.strptime(form_data['fecha_nacimiento'], "%d/%m/%Y")]
            if form_data["tiene_hijos"].lower().startswith("s"):
                df["tiene_hijos"] = "Sí"
                df["n_hijos"] = "4+" if form_data['n_hijos'] == "4+" else int(form_data['n_hijos'])
            else:
                df["tiene_hijos"] = "No"
                df["n_hijos"] = None

            df["edad_jubilacion_deseada"] = int(form_data['edad_jubilacion'])

            

            columnas_restantes = ['gender', 'salario_medio', 'edad_inicio_trabajo', 'r_cotizacion']
            for columna in columnas_restantes:
                df[columna] = form_data[columna]

            if form_data["lagunas_cotizacion"].lower().startswith("s"):
                df["n_lagunas"] = form_data["n_lagunas"]

            logging.info("DataFrame filtrado: %s", df)

            if not df.empty:
                form_data = df.iloc[0].to_dict()
            else:
                logging.error("No se encontraron registros que coincidan con los criterios.")
                return

            logging.info("Datos filtrados: %s", form_data)
            pension = await calcular_pension_1p(form_data)
            self.form_data = form_data
            logging.info(f"Pensión calculada: {pension}")
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e

def form1():
    return rx.form(
        rx.vstack(
            date_picker("Fecha de nacimiento"),
            gender(),
            input_text("Salario medio obtenido","salario_medio", AvgSalaryState, "number"),
            children(),
            input_text("Edad a la que empezaste a cotizar","edad_inicio_trabajo", StartAgeState, "number"),
            input_text("Edad deseada de jubilación", "edad_jubilacion",AgeState, "number"),
            tipo_regimen(),
            rx.hstack(
                rx.button(
                    "Limpiar formulario",
                    type="button",
                    on_click=FormState.clear_form,
                    color="white",
                    width="50%",
                    border="1px solid",
                    box_shadow="0 .25rem .375rem #0003",
                    background_color=color.BACKGROUND.value,
                    _hover={"bg": color.SECONDARY.value, "color": "white"}
                ),
                rx.button("Siguiente", 
                        type="submit",
                        background_color="white",
                        color=color.BACKGROUND.value,
                        width="50%",
                        border="1px solid",
                        box_shadow="0 .25rem .375rem #0003",
                        _hover={"bg": color.SECONDARY.value, "color": "white"}
                ),
                
                width="100%",
                spacing="4"
                
            ),
            width="100%",
            spacing="5",
            padding=["1em", "1.5em", "2em"],
            max_width="100%",
            font_weight='bold'
        ),
        on_submit=FormState.handle_submit,
        value=FormState.stored_form_data,
        margin_top=size.DEFAULT.value,
        align="center",
        width="100%",
    )

def form1_():
    return rx.cond(
        rx.State.is_hydrated,
        rx.vstack(
            rx.vstack(
                rx.heading(
                    "Simulador de pensiones",
                    color="white",
                    font_family=Font.TITLE.value,
                    font_size=size.BIG.value,
                    font_weight="bold",
                    margin_top=size.SMALL.value,
                ),
                form1(),
                overflow="hidden",
                align="center",
                padding="1em",
                height="100%",
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            padding="10em"
        )
    )