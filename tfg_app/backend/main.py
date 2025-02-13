from pydantic import BaseModel
from tfg_app.backend.pens import calcular_primer_pilar,estimar_tiempo_cotizado, calcular_segundo_pilar
import datetime
import reflex as rx
from datetime import datetime


class FormData(BaseModel):
    fecha_nacimiento:str
    gender: str
    tiene_hijos: str
    n_hijos: str
    salario_medio: float  # Asegúrate de incluir otros campos necesarios
    edad_inicio_trabajo: float  # Por ejemplo, la edad al comenzar a trabajar
    edad_jubilacion_deseada: float  # La edad a la que se desea jubilar
    r_cotizacion: str
    lagunas_cotizacion: str
    n_lagunas: int

class FormData2(BaseModel):
    prev_form: FormData
    quiere_aportar: str
    aportacion_empresa: float



async def calcular_pension_1p(data: FormData):

    #edad_actual = calcular_edad(fecha_nacimiento)
    annos_cotizados = estimar_tiempo_cotizado(data['fecha_nacimiento'], data['edad_inicio_trabajo'],data['edad_jubilacion_deseada'])
    #tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, data.edad_jubilacion_deseada, annos_cotizados)
    #anno_jubilacion = datetime.date.today().year + (data.edad_jubilacion_deseada - edad_actual)
    pension_primer_pilar = calcular_primer_pilar(float(data['salario_medio']), annos_cotizados, data['tiene_hijos'],data['n_hijos'])

    return round(pension_primer_pilar,2)

async def calcular_pension_2p(data: dict):
    # Convertir el diccionario a una instancia de FormData2
    form_data = FormData2(**data)  # Desempaquetar el diccionario
    pension_segundo_pilar = calcular_segundo_pilar(
        salario_actual=form_data.prev_form.salario_medio,  # Acceder como un diccionario
        categoria=2,
        aportacion_voluntaria_ppe=2 if form_data.quiere_aportar.lower().startswith("s") else 0,
        ppe_porcentaje_empresa=form_data.aportacion_empresa
    )
    return round(pension_segundo_pilar, 2)