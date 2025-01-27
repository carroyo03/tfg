import reflex as rx
from tfg_app.styles.colors import Color as color
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.seg_pilar.aportaciones import Employee2PState, aportar
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

class FormState(rx.State):
    form_data: dict = {}
    
    @rx.var
    def stored_form_data(self) -> dict:
        """Una computed var que maneja los datos del formulario."""
        return self.form_data

    ####################################################################
    #### Cambiar handle_submit para adaptarlo al segundo formulario ####
    ####################################################################

    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            form_data['fecha_nacimiento'] = f"{form_data['day']}/{form_data['month']}/{form_data['year']}"
            del form_data['day']
            del form_data['month']
            del form_data['year']
            self.form_data = form_data
            
            pension = await self.send_data_to_backend(form_data)
            state = await self.get_state(GlobalState)
            state.set_pension_segundo_pilar(pension)
            return rx.redirect("/pilar1")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    @rx.event
    async def clear_form(self):
        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [Employee2PState, Company2PState]:
            state= await self.get_state(state_class)
            await state.reset_values()
        
        # Fuerza actualización del frontend
        return rx.call_script("window.location.reload();")
    
     

    

def form2():
    return rx.form(
        rx.vstack(
            input_text("Aportación anual de la empresa al PPE","aportacion_empresa", Company2PState,"number"),
            aportar(f"¿Quieres aportar un 2% a tu plan de pensiones de la empresa?"),
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
        align="center",
    )

def form2_():
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "Simulador de pensiones: 2º Pilar",
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
    )
