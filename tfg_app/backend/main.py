from pydantic import BaseModel
from tfg_app.backend.pens import calcular_base_reguladora, calcular_primer_pilar,estimar_tiempo_cotizado, calcular_pension_segundo_pilar, calcular_pension_tercer_pilar


import datetime
import reflex as rx
import torch #type:ignore
import torch.nn as nn #type:ignore
from tfg_app.backend.predictions.neural_network import PensionPredictor, preprocess_input, get_recommendations #type:ignore



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
    n_lagunas: float

class FormData2(BaseModel):
    prev_form: FormData
    quiere_aportar: str
    aportacion_empresa: float
    rentabilidad_2: int


class FormData3(BaseModel):
    prev_form: FormData2
    aportacion_empleado_3p: float
    rentabilidad_3: int

def calcular_edad(fecha_nacimiento):
    fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
    return int(datetime.datetime.today().year - fecha_nacimiento.year)

def annos_por_trabajar(edad_actual,edad_jubilacion_deseada):
    return int(edad_jubilacion_deseada - edad_actual)

async def calcular_pension_1p(data: dict):
    # Accept dictionary input instead of FormData
    # Convert dictionary to FormData if needed
    if not isinstance(data, dict):
        data = data.dict()  # Convert FormData to dict if it's not already a dict

    #edad_actual = calcular_edad(fecha_nacimiento)
    annos_cotizados = estimar_tiempo_cotizado(data['fecha_nacimiento'], data['edad_inicio_trabajo'], data['edad_jubilacion_deseada'])
    #tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, data.edad_jubilacion_deseada, annos_cotizados)
    #anno_jubilacion = datetime.date.today().year + (data.edad_jubilacion_deseada - edad_actual)
    
    # Determinar si hay lagunas de cotización
    # Si el usuario indica que tiene lagunas, usamos el valor proporcionado; de lo contrario, 0.
    if 'n_lagunas' in data and data['n_lagunas'] is not None:
        print(f"Hay {data['n_lagunas']} lagunas")
        lagunas = float(data['n_lagunas'])
    else:
        lagunas = 0
    
    # Determinar el tipo de cotización y el género
    tipo_trabajador = data['r_cotizacion']  # Por ejemplo, "General"
    es_mujer = True if data['gender'].lower().startswith("m") else False

    # Calcular la base reguladora a partir de los últimos 25 años
    base_reguladora = calcular_base_reguladora(
        salario_anual = float(data['salario_medio']),
        annos_sin_cotizar = lagunas,
        tipo_trabajador = tipo_trabajador,
        es_mujer = es_mujer,
        annos_a_incluir = 25,
        num_pagas = 14
    )
    print(f"Base reguladora: {base_reguladora}")
    
    # Ensure we pass edad_deseada parameter correctly
    pension_primer_pilar = calcular_primer_pilar(
        base_reguladora=base_reguladora, 
        annos_cotizados=annos_cotizados, 
        tiene_hijos=data['tiene_hijos'],
        num_hijos=data['n_hijos'],
        edad_deseada=data['edad_jubilacion_deseada']
    )
    
    print(f"Pensión primer pilar: {pension_primer_pilar}")

    return round(pension_primer_pilar,2)

async def calcular_pension_2p(data: dict):
    # Convertir el diccionario a una instancia de FormData2
    form_data = FormData2(**data)  # Desempaquetar el diccionario
    edad_actual = calcular_edad(form_data.prev_form.fecha_nacimiento)
    pension_segundo_pilar = calcular_pension_segundo_pilar(
        salario_anual=form_data.prev_form.salario_medio,  # Acceder como un diccionario
        aportacion_empleado_voluntaria=2 if form_data.quiere_aportar.lower().startswith("s") else 0,
        aportacion_empleador=form_data.aportacion_empresa,
        edad_jubilacion=form_data.prev_form.edad_jubilacion_deseada,
        periodo_aportacion_annos=annos_por_trabajar(edad_actual, form_data.prev_form.edad_jubilacion_deseada),
        rentabilidad_anual_esperada=form_data.rentabilidad_2/100  # ¡habrá que cambiar esto
    )
    return round(pension_segundo_pilar, 2)


async def calcular_pension_3p(data:dict):

    form_data = FormData3(**data)
    first_form_data = form_data.prev_form.prev_form
    edad_actual = calcular_edad(first_form_data.fecha_nacimiento)
    pension_tercer_pilar = calcular_pension_tercer_pilar(
        aportacion_periodica=form_data.aportacion_empleado_3p,
        edad_jubilacion=first_form_data.edad_jubilacion_deseada,
        rentabilidad_anual_esperada=form_data.rentabilidad_3/100,  #Cambiar esto
        periodo_aportacion_annos=annos_por_trabajar(edad_actual, first_form_data.edad_jubilacion_deseada)
    )

    return round(pension_tercer_pilar, 2)

async def get_pension_recommendations(data:dict):
    model = PensionPredictor()
    model.load_state_dict(torch.load("pension_model.pth"))
    model.eval()
    with torch.no_grad():
        inputs = preprocess_input(data)
        scores = model(inputs)
        recommendations = get_recommendations(scores)
        return recommendations