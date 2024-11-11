from fastapi import FastAPI
from pydantic import BaseModel
from ..pens import calcular_primer_pilar,calcular_edad,estimar_bases_cotizacion,estimar_tiempo_cotizado,calc  # Asegúrate de importar la función correcta
import datetime
app = FastAPI()

class FormData(BaseModel):
    day: str
    month: str
    year: str
    gender: str
    tiene_hijos: str
    n_hijos: str
    edad_jubilacion: str
    salario_actual: float  # Asegúrate de incluir otros campos necesarios
    edad_inicio_trabajo: float  # Por ejemplo, la edad al comenzar a trabajar
    porcentaje_personal: float  # Porcentaje del segundo pilar
    porcentaje_empresa: float  # Porcentaje de la empresa en el segundo pilar
    contribucion_privada: float  # Contribución al tercer pilar
    rendimiento_privado: float  # Rendimiento del tercer pilar

@app.post("/calcular_pension/")
async def calcular_pension(data: FormData):
    # Llama a la función de cálculo de pensiones
    fecha_nacimiento = f"{data.day}/{data.month}/{data.year}".date()
    edad_actual = calcular_edad(fecha_nacimiento)
    annos_cotizados, meses_cotizados, _ = estimar_tiempo_cotizado(fecha_nacimiento, edad_inicio_trabajo)
    tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, edad_jubilacion_deseada, annos_cotizados)
    anno_jubilacion = datetime.date.today().year + (edad_jubilacion_deseada - edad_actual)
    pension_primer_pilar = calcular_primer_pilar(salario, annos_cotizados, meses_cotizados, df_annual_cpi, tipo_jubilacion, meses_ajuste, anno_jubilacion, genero, numero_hijos)
    return {"pension_total": pension_total}