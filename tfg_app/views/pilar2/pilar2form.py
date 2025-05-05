import reflex as rx #type:ignore
from tfg_app.backend.pens import RatioSust2
from tfg_app.components.slider import SliderState, rentabilidad_estimada
from tfg_app.styles.colors import Color as color
from tfg_app.components.seg_pilar.aportaciones import Employee2PState, aportar
from tfg_app.views.pilar1.pilar1results import FormState
from tfg_app.components.input_text import input_text
from tfg_app.global_state import GlobalState
from tfg_app.components.seg_pilar.aportaciones import Company2PState
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
            # Obtener el estado global
            global_state = await self.get_state(GlobalState)
            
            # Verificar que existen datos del primer pilar
            if not hasattr(global_state, 'form_data_primer_pilar') or not global_state.form_data_primer_pilar:
                logging.error("No se encontraron datos del primer pilar")
                return rx.window_alert("Error: No se encontraron datos del primer pilar. Por favor, complete el primer formulario.")
                
            prev_form_data = global_state.form_data_primer_pilar
            
            # Convertir fecha_nacimiento a string si es necesario
            if isinstance(prev_form_data.get('fecha_nacimiento'), datetime.datetime):
                prev_form_data['fecha_nacimiento'] = prev_form_data['fecha_nacimiento'].strftime("%d/%m/%Y")
            
            # Asegurarse de que todos los campos necesarios existen
            if 'tiene_hijos' in prev_form_data:
                if prev_form_data['tiene_hijos'].lower().startswith('s'):
                    prev_form_data['n_hijos'] = str(prev_form_data.get('n_hijos', '0'))
                else:
                    prev_form_data['n_hijos'] = '0'
            
            if 'edad_jubilacion_deseada' in prev_form_data:
                prev_form_data['edad_jubilacion_deseada'] = str(prev_form_data['edad_jubilacion_deseada'])
            
            if 'lagunas_cotizacion' in prev_form_data:
                if prev_form_data['lagunas_cotizacion'].lower().startswith('s'):
                    prev_form_data['n_lagunas'] = str(prev_form_data.get('n_lagunas', '0'))
                else:
                    prev_form_data['n_lagunas'] = '0'
            
            # Crear el nuevo diccionario con los datos requeridos
            self.form_data['prev_form'] = prev_form_data
            
            # Asegurarse de que aportacion_empleado esté presente
            self.form_data['aportacion_empleado'] = form_data.get('aportacion_empleado', 0)
            
            # Actualizar con los nuevos datos del formulario
            self.form_data.update(form_data)
            
            # Calcular la pensión
            pension = await self.send_data_to_backend(self.form_data)
            
            # Verificar que se obtuvo un valor válido
            if pension <= 0:
                logging.error(f"Pensión calculada inválida: {pension}")
                return rx.window_alert("Error al calcular la pensión. Por favor, revise los datos ingresados.")
            
            # Calcular el ratio de sustitución
            ratio_state = await self.get_state(RatioSust2)
            
            # Asegurarse de que salario_medio es un número
            salario_medio = float(prev_form_data.get('salario_medio', 0))
            if salario_medio <= 0:
                logging.error(f"Salario medio inválido: {salario_medio}")
                return rx.window_alert("Error: Salario medio inválido. Por favor, revise los datos ingresados.")
            
            # Calcular el ratio
            ratio_state.calcular_ratio(salario=salario_medio / 12, pension=pension)
            
            # Guardar los datos en el estado global
            global_state.set_form_data("segundo", self.form_data)
            global_state.set_pension("segundo", pension)
            
            # Redirigir a la página de resultados
            return rx.redirect("/pilar2")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}", exc_info=True)
            return rx.window_alert(f"Error al procesar el formulario: {str(e)}")

    @rx.event
    async def clear_form(self):
        self.is_loading = True
        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [Employee2PState, Company2PState, SliderState]:
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
            form_data = form_data_prev
            
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
            
            # Asegurarse de que salario_medio es un número
            salario_medio = float(form_data['prev_form']['salario_medio'])
            
            ratio_state = await self.get_state(RatioSust2)
            ratio_state.calcular_ratio(salario=salario_medio/12, pension=pension)
            print(f"2st ratio: {ratio_state.ratio}")
            
            state = await self.get_state(GlobalState)
            state.set_form_data("segundo", self.form_data)
            state.set_pension("segundo", pension)
            return pension
        except Exception as e:
            logging.error(f"Error al enviar datos al backend: {e}")
            raise e

    

def form2(is_mobile:bool=False):
    if not is_mobile:
        width_button_var='50%'
        padding_value='0'
    else:
        width_button_var='100%'
        padding_value=["1em", "1.5em", "2em"]
    return rx.form(
        rx.vstack(
            input_text("Aportación anual de la empresa al PPE (%)","aportacion_empresa", Company2PState,"number"),
            aportar(f"¿Quieres aportar un 2% a tu plan de pensiones de la empresa?"),
            rentabilidad_estimada(2),
            rx.stack(
                rx.button(
                    "Limpiar",
                    type="button",
                    on_click=Form2State.clear_form,
                    color="white",
                    width=width_button_var,
                    border="1px solid",
                    box_shadow="0 .25rem .375rem #0003",
                    background_color=color.BACKGROUND.value,
                    _hover={"bg": color.SECONDARY.value, "color": "white"}
                ),
                rx.button("Siguiente", 
                        type="submit",
                        background_color="white",
                        color=color.BACKGROUND.value,
                        width=width_button_var,
                        border="1px solid",
                        box_shadow="0 .25rem .375rem #0003",
                        _hover={"bg": color.SECONDARY.value, "color": "white"}
                ),
                
                width="100%",
                spacing="4",
                direction=rx.breakpoints(initial='column', sm='row')
                
            ),
            width="100%",
            spacing="5",
            padding=padding_value,
            max_width="100%",
            font_weight='bold',
            justify='center'
        ),
        on_submit=Form2State.handle_submit,
        value=Form2State.stored_form_data,
        width="100%",
        height="auto",
        margin='0 auto'
    )
