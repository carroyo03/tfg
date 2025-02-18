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
from tfg_app.views.pilar2.pilar2form import Form2State
from tfg_app.components.terc_pilar.aportaciones import Employee3PState

import pandas as pd
import datetime
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO)

class Form3State(rx.State):
    form_data: dict = {}
    is_loading: bool = False

    @rx.var
    def stored_form_data(self) -> dict:
        """Una computed var que maneja los datos del formulario."""
        return self.form_data

    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            prev_form_state = await self.get_state(Form2State)
            fecha_nacimiento = prev_form_state.stored_form_data['prev_form']['fecha_nacimiento'].strftime("%d/%m/%Y")  # Convertir a string
            n_hijos = str(prev_form_state.stored_form_data['prev_form'].get('n_hijos', '0'))  # Usar '0' si es None
            edad_jubilacion = str(prev_form_state.stored_form_data['prev_form']['edad_jubilacion_deseada'])  # Convertir a string
            
            self.form_data['prev_form'] = {
                'fecha_nacimiento': fecha_nacimiento,
                'tiene_hijos': prev_form_state.stored_form_data['prev_form']['tiene_hijos'],
                'n_hijos': n_hijos,
                'edad_jubilacion_deseada': edad_jubilacion,  # Asegúrate de que este campo esté presente
                'gender': prev_form_state.stored_form_data['prev_form']['gender'],
                'salario_medio': prev_form_state.stored_form_data['prev_form']['salario_medio'],
                'edad_inicio_trabajo': prev_form_state.stored_form_data['prev_form']['edad_inicio_trabajo'],
                'r_cotizacion': prev_form_state.stored_form_data['prev_form']['r_cotizacion'],
                'lagunas_cotizacion': prev_form_state.stored_form_data['prev_form'].get('lagunas_cotizacion', ''),  # Asegúrate de que este campo esté presente
                'n_lagunas': prev_form_state.stored_form_data['prev_form'].get('n_lagunas', 0),  # Asegúrate de que este campo esté presente
                'aportacion_empresa': prev_form_state.stored_form_data.get('aportacion_empresa',0),
                'quiere_aportar': prev_form_state.stored_form_data.get('quiere_aportar','No'),
                'aportacion_empleado_2p': prev_form_state.stored_form_data.get('aportacion_empleado',0)
            }

            self.form_data['aportacion_empleado_3p'] = form_data.get('aportacion_empleado_3p',0)

            self.form_data.update(form_data)

            pension = await self.send_data_to_backend(form_data)
            state = await self.get_state(GlobalState)
            state.set_pension("tercer",pension)
            return rx.redirect("/results")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    @rx.event
    async def clear_form(self):
        self.is_loading = True
        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [Employee3PState]:
            state= await self.get_state(state_class)
            await state.reset_values()
        
        # Fuerza actualización del frontend
        return rx.call_script("window.location.reload();")
    

    def default_fields(self):
        yield Employee3PState

    async def send_data_to_backend(self, form_data: dict):
        from tfg_app.backend.main import calcular_pension_tercer_pilar
        try:
           
            logging.info("Valores de form_data: %s", form_data)

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
            pension = await calcular_pension_tercer_pilar(form_data)
            self.form_data = form_data
            logging.info(f"Pensión calculada: {pension}")
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e

def form3():
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
                    on_click=Form3State.clear_form,
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
        on_submit=Form3State.handle_submit,
        value=Form3State.stored_form_data,
        margin_top=size.DEFAULT.value,
        align="center",
    )

def form3_():
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
                    form3(),
                    overflow="hidden",
                    align="center",
                    padding="1em",
                    height="100%",
                ),
        ),
        rx.center(
            rx.spinner(size="9"),
            padding="10em"
        )
    )
