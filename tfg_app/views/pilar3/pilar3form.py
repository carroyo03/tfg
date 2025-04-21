import reflex as rx
from tfg_app.backend.pens import RatioSust3
from tfg_app.components.slider import rentabilidad_estimada
from tfg_app.styles.colors import Color as color
from tfg_app.styles.styles import Size as size
from tfg_app.components.input_text import input_text
from tfg_app.global_state import GlobalState
from tfg_app.views.pilar2.pilar2form import Form2State
from tfg_app.components.terc_pilar.aportaciones import Employee3PState

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
            prev_form_data = prev_form_state.stored_form_data
            self.form_data['prev_form'] = {
                'first_form':prev_form_data['prev_form'],
                'aportacion_empresa': prev_form_state.stored_form_data.get('aportacion_empresa',0),
                'quiere_aportar': prev_form_state.stored_form_data.get('quiere_aportar','No'),
                'aportacion_empleado_2p': prev_form_state.stored_form_data.get('aportacion_empleado',0)
            }

            self.form_data['aportacion_empleado_3p'] = form_data.get('aportacion_empleado_3p',0)

            self.form_data.update(form_data)

            pension = await self.send_data_to_backend(form_data)
            ratio_state = await self.get_state(RatioSust3)
            ratio_state.calcular_ratio(salario=self.form_data['prev_form']['first_form']['salario_medio'], pension=pension)
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

    async def send_data_to_backend(self, form_data_prev: dict):
        from tfg_app.backend.main import calcular_pension_3p
        try:
           

            form_data = {}
            prev_form_state = await self.get_state(Form2State)
            form_data['prev_form'] = prev_form_state.stored_form_data
            form_data.update(form_data_prev)
            logging.info("Valores de form_data: %s", form_data)

            logging.info("Datos filtrados: %s", form_data)
            pension = await calcular_pension_3p(form_data)
            self.form_data = form_data
            logging.info(f"Pensión calculada: {pension}")
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e




def form3():
    return rx.form(
        rx.vstack(
            input_text("Aportación anual al plan privado de pensiones (€)","aportacion_empleado_3p", Employee3PState,"number"),
            rentabilidad_estimada(3),
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


