import reflex as rx
from tfg_app.components.slider import rentabilidad_estimada
from tfg_app.styles.colors import Color as color
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.seg_pilar.aportaciones import Employee2PState, aportar
from tfg_app.views.pilar1.pilar1results import FormState
from tfg_app.components.input_text import input_text, AgeState, StartAgeState, AvgSalaryState
from tfg_app.components.date_input_text import date_picker, DateState
from tfg_app.components.gender import gender, GenderState
from tfg_app.global_state import GlobalState
from tfg_app.components.children import children, RadioGroupState, ChildrenNumberState
from tfg_app.components.tipo_regimen import tipo_regimen, RadioGroup1State, TypeRegState, LagsCotState
from tfg_app.components.seg_pilar.aportaciones import Company2PState
from tfg_app.styles.styles import BASE_STYLE
from tfg_app.views.pilar1.pilar1results import results_pilar1






import pandas as pd
import datetime
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO)

class Form2State(rx.State):
    form_data: dict = {}
    is_loading: bool = False
    
    @rx.var
    def stored_form_data(self) -> dict:
        """Una computed var que maneja los datos del formulario."""
        return self.form_data


    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            prev_form_state = await self.get_state(FormState)
            
            # Convertir fecha_nacimiento a string
            fecha_nacimiento = prev_form_state.stored_form_data['fecha_nacimiento'].strftime("%d/%m/%Y")  # Convertir a string
            
            # Asegurarse de que n_hijos tenga un valor válido
            n_hijos = str(prev_form_state.stored_form_data.get('n_hijos', '0'))  # Usar '0' si es None
            
            # Asegurarse de que edad_jubilacion sea una cadena
            edad_jubilacion = str(prev_form_state.stored_form_data['edad_jubilacion_deseada'])  # Convertir a string
            
            # Crear el nuevo diccionario con los datos requeridos
            self.form_data['prev_form'] = {
                'fecha_nacimiento': fecha_nacimiento,
                'tiene_hijos': prev_form_state.stored_form_data['tiene_hijos'],
                'n_hijos': n_hijos,
                'edad_jubilacion_deseada': edad_jubilacion,  # Asegúrate de que este campo esté presente
                'gender': prev_form_state.stored_form_data['gender'],
                'salario_medio': prev_form_state.stored_form_data['salario_medio'],
                'edad_inicio_trabajo': prev_form_state.stored_form_data['edad_inicio_trabajo'],
                'r_cotizacion': prev_form_state.stored_form_data['r_cotizacion'],
                'lagunas_cotizacion': prev_form_state.stored_form_data.get('lagunas_cotizacion', ''),  # Asegúrate de que este campo esté presente
                'n_lagunas': prev_form_state.stored_form_data.get('n_lagunas', 0)  # Asegúrate de que este campo esté presente
            }
            
            # Asegúrate de que aportacion_empleado esté presente
            self.form_data['aportacion_empleado'] = form_data.get('aportacion_empleado', 0)  # Usar 0 si no está presente
            
            self.form_data.update(form_data)
            
            pension = await self.send_data_to_backend(self.form_data)
            state = await self.get_state(GlobalState)
            state.set_pension("segundo",pension)
            return rx.redirect("/pilar2")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    @rx.event
    async def clear_form(self):
        self.is_loading = True
        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [Employee2PState, Company2PState]:
            state= await self.get_state(state_class)
            await state.reset_values()
        
        # Fuerza actualización del frontend
        return rx.call_script("window.location.reload();")
    
    def default_fields(self):
        yield Employee2PState
        yield Company2PState

    async def send_data_to_backend(self, form_data_prev: dict):
        from tfg_app.backend.main import calcular_pension_2p
        try:
            """
            df_users = pd.read_csv('usuarios.csv', encoding='unicode_escape', sep=';')
            df_users['fecha_nacimiento'] = pd.to_datetime(df_users['fecha_nacimiento'], format='%d-%m-%Y')
            logging.info("DataFrame cargado: %s", df_users)
 """        
            form_data = {}
            prev_form_state = await self.get_state(FormState)
            form_data['prev_form'] = prev_form_state.stored_form_data
            form_data.update(form_data_prev)
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

            
            logging.info("Datos filtrados: %s", form_data)
            pension = await calcular_pension_2p(form_data)
            self.form_data = form_data
            logging.info(f"Pensión calculada: {pension}")
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e

    

def form2():
    return rx.form(
        rx.vstack(
            input_text("Aportación anual de la empresa al PPE","aportacion_empresa", Company2PState,"number"),
            aportar(f"¿Quieres aportar un 2% a tu plan de pensiones de la empresa?"),
            rentabilidad_estimada(),
            rx.hstack(
                rx.button(
                    "Limpiar formulario",
                    type="button",
                    on_click=Form2State.clear_form,
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
        on_submit=Form2State.handle_submit,
        value=Form2State.stored_form_data,
        align="center",
    )

def form2_():
    return rx.cond(
        rx.State.is_hydrated,
        rx.vstack(
                rx.vstack(
                    rx.heading(
                        "Simulador de pensiones: Pensión de empresa",
                        color="white",
                        font_family=Font.TITLE.value,
                        font_size=size.LARGE.value,
                        font_weight="bold",
                        margin_top=size.SMALL.value,
                    ),
                    form2(),
                    overflow="hidden",
                    align="center",
                    padding="1em",
                    height="100%",
                ),
                align="center"
        ),
        rx.center(
            rx.spinner(size="9"),
            padding="10em"
        )
    )
