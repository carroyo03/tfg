import reflex as rx #type: ignore
from tfg_app.backend.pens import RatioSust1
from tfg_app.styles.colors import Color as color
from tfg_app.components.input_text import input_text, AgeState, StartAgeState, AvgSalaryState
from tfg_app.components.date_input_text import date_picker, DateState
from tfg_app.components.gender import gender, GenderState
from tfg_app.global_state import GlobalState
from tfg_app.components.children import children, RadioGroupState, ChildrenNumberState
from tfg_app.components.tipo_regimen import tipo_regimen, RadioGroup1State, TypeRegState, LagsCotState
import pandas as pd #type: ignore
import datetime
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO)

class FormState(rx.State):
    form_data: dict = {}
    is_loading: bool = False
    salario_medio: float = 0.0
    salario_mensual: float = 0.0

    def update_salario_mensual(self):
        print(f"Updating average salary to {self.form_data.get('salario_medio')} or {self.form_data['salario_medio']}")
        # Asegurarse de que salario_medio existe y es un número válido
        if 'salario_medio' in self.form_data and self.form_data['salario_medio'] is not None:
            try:
                self.salario_medio = float(self.form_data.get("salario_medio", 0))
                self.form_data["salario_medio"] = self.salario_medio
                print(f"Current average salary: {self.salario_medio}")
                self.salario_mensual = self.salario_medio / 12
                self.form_data["salario_mensual"] = self.salario_mensual
                print(f"Monthly average salary updated: {self.salario_mensual}")
            except (ValueError, TypeError) as e:
                raise Exception(f"Error al convertir salario_medio: {e}")
                """self.salario_medio = 0.0
                self.salario_mensual = 0.0
                self.form_data["salario_medio"] = 0.0
                self.form_data["salario_mensual"] = 0.0"""
        else:
            raise Exception("salario_medio no está definido en form_data")
            """self.salario_medio = 0.0
            self.salario_mensual = 0.0
            self.form_data["salario_medio"] = 0.0
            self.form_data["salario_mensual"] = 0.0
            """

    
    @rx.var
    def stored_form_data(self) -> dict:
        """Una computed var que maneja los datos del formulario."""
        return self.form_data

    @rx.var
    async def invalid_form_data(self) -> bool:
        """Returns True if the form has invalid or empty required fields."""
        try:
            # Debug output
            print("Checking form validation...")
            
            # Check each state individually for better debugging
            gender_state = await self.get_state(GenderState)
            if gender_state.empty_value:
                print("Gender is empty")
                return True
                
            date_state = await self.get_state(DateState)
            if date_state.invalid_value:
                print("Date is empty")
                return True
                
            salary_state = await self.get_state(AvgSalaryState)
            if salary_state.empty_value or salary_state.invalid_value:
                print("Salary is empty or invalid")
                return True
                
            # Check children state
            radio_group_state = await self.get_state(RadioGroupState)
            if radio_group_state.empty:
                print("Children radio is empty")
                return True
                
            # Only check number of children if they have children
            if radio_group_state.item == "Sí":
                children_number_state = await self.get_state(ChildrenNumberState)
                if children_number_state.empty_value:
                    print("Number of children is empty")
                    return True
            
            # Check start age
            start_age_state = await self.get_state(StartAgeState)
            if start_age_state.empty_value:
                print("Start age is empty")
                return True
            elif start_age_state.invalid_value:
                print("Start age is invalid")
                return True
                
            # Check retirement age
            age_state = await self.get_state(AgeState)
            if age_state.empty_value:
                print("Retirement age is empty")
                return True
            elif age_state.invalid_value:  # Changed to elif to avoid double checking
                print("Retirement age is invalid")
                return True
            
            if not start_age_state.empty_value and not age_state.empty_value:
                # Check minimum years of contribution only if both values are valid numbers
                try:
                    if int(age_state.value) - int(start_age_state.value) < 15:
                        print("Años insuficientes de cotización")
                        return True
                except ValueError:
                    # If conversion fails, we'll catch it in the individual field validations
                    pass
                
                
                
            # Check regime type
            type_reg_state = await self.get_state(TypeRegState)
            if type_reg_state.empty_value:
                print("Type reg is empty")
                return True
                
            # Check contribution gaps
            lags_radio_state = await self.get_state(RadioGroup1State)
            if lags_radio_state.empty_value:
                print("Contribution gaps radio is empty")
                return True
                
            # Only check number of gaps if they have gaps
            if lags_radio_state.item == "Sí":
                lags_cot_state = await self.get_state(LagsCotState)
                if lags_cot_state.empty_value:
                    print("Number of contribution gaps is empty")
                    return True
            
            # If we get here, the form is valid
            print("Form is valid!")
            return False
        except Exception as e:
            print(f"Error validating form: {e}")
            return True  # If there's an error, disable the button
    
    @rx.event
    async def handle_submit(self, form_data: dict):
        try:
            print("Handling form submission...")
            # Need to await the async computed variable
            is_invalid = await self.invalid_form_data
            if is_invalid:
                raise ValueError("Datos del formulario inválidos")
            
            form_data['fecha_nacimiento'] = f"{form_data['day']}/{form_data['month']}/{form_data['year']}"
            del form_data['day']
            del form_data['month']
            del form_data['year']
            self.form_data = form_data

            self.update_salario_mensual()
    
            pension = await self.send_data_to_backend(self.form_data)
            
            # Verificar que pension y salario_mensual son valores válidos
            if pension is not None and self.salario_mensual > 0:
                ratio_state = await self.get_state(RatioSust1)
                ratio_state.calcular_ratio(salario=self.salario_mensual, pension=pension)
                print(f"1st ratio: {ratio_state.ratio}")
                state = await self.get_state(GlobalState)
                state.set_form_data("primer", self.form_data)
                state.set_pension("primer", pension)
                return rx.redirect("/pilar1")
            else:
                raise ValueError("Pensión o salario mensual inválidos")
        except Exception as e:
            logging.error(f"Error en handle_submit: {e}")
            return rx.window_alert("Error al procesar el formulario")

    @rx.event
    async def clear_form(self):

        self.is_loading = True

        # Limpia el estado principal
        self.form_data = {}
        
        # Limpia los substates
        for state_class in [AgeState, GenderState, DateState, RadioGroupState, StartAgeState,
                            ChildrenNumberState,RadioGroup1State, TypeRegState,
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

            

            columnas_restantes = ['gender', 'salario_medio', 'edad_inicio_trabajo', 'r_cotizacion', 'lagunas_cotizacion']
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
            input_text(
                title="Salario medio obtenido",
                name="salario_medio",
                state=AvgSalaryState,
                type_="number",
                has_info_button=True,
                info="Introduce el salario bruto medio obtenido anualmente",
                color_info_button="white",
            ),
            children(),
            input_text("Edad a la que empezaste a cotizar", "edad_inicio_trabajo", StartAgeState, "number"),
            input_text("Edad deseada de jubilación", "edad_jubilacion", AgeState, "number"),
            tipo_regimen(),
            # Botones con position: sticky
            rx.stack(
                rx.button(
                        "Limpiar",
                        type="reset",
                        background_color=color.BACKGROUND.value,
                        color="white",
                        width=rx.breakpoints(initial="100%", sm="48%"),
                        border="1px solid",
                        box_shadow="0 .25rem .375rem #0003",
                        border_radius="0.5em",
                        padding=rx.breakpoints(initial="1em", sm="1.2em"),
                        font_size=rx.breakpoints(initial="1em", sm="1.1em"),
                        _hover={"bg": color.SECONDARY.value, "color": "white"},
                        on_click=FormState.clear_form,
                ),
                rx.button(
                    "Siguiente",
                    type="submit",
                    background_color="white",
                    color=color.BACKGROUND.value,
                    width=rx.breakpoints(initial="100%", sm="48%"),
                    border="1px solid",
                    box_shadow="0 .25rem .375rem #0003",
                    border_radius="0.5em",
                    padding=rx.breakpoints(initial="1em", sm="1.2em"),
                    font_size=rx.breakpoints(initial="1em", sm="1.1em"),
                    _hover={"bg": color.SECONDARY.value, "color": "white"},
                    disabled=FormState.invalid_form_data,
                ),
                direction=rx.breakpoints(initial="column", sm="row"),
                spacing="3",
                width="100%",
                align_items="stretch",
                justify_content="center",
                position="sticky",
                bottom="1rem",
                z_index="10",
                padding="1rem",
            ),
            spacing="8",
            padding=rx.breakpoints(initial="1em", sm="1.5em", md="2em"),
            padding_bottom="5rem",  # Espacio extra para los botones
            width="100%",
            height="auto",  # Permitir que el formulario crezca según el contenido
            min_height="100vh",  # Asegurar que ocupe al menos la pantalla
            overflow_y="auto",  # Permitir desplazamiento vertical
        ),
        on_submit=FormState.handle_submit,
        value=FormState.stored_form_data,
        align="center",
        padding=rx.breakpoints(initial='1em', sm='1.1em'),
        width="100%",
        font_weight="bold"
    )