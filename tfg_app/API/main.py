from fastapi import FastAPI
from pydantic import BaseModel
from ..pens import calcular_primer_pilar,calcular_edad,estimar_tiempo_cotizado,DF_CPI,calcular_annos_anticipacion_o_demora 
import datetime
app = FastAPI()

class FormData(BaseModel):
    date:str
    gender: str
    tiene_hijos: str
    n_hijos: str
    edad_jubilacion: str
    salario_actual: float  # Asegúrate de incluir otros campos necesarios
    edad_inicio_trabajo: float  # Por ejemplo, la edad al comenzar a trabajar
    edad_jubilacion_deseada: float  # La edad a la que se desea jubilar

@app.post("/calcular_pension/")
async def calcular_pension(data: FormData):
    # Llama a la función de cálculo de pensiones
    fecha_nacimiento = f"{data.date}".date()
    edad_actual = calcular_edad(fecha_nacimiento)
    annos_cotizados, meses_cotizados, _ = estimar_tiempo_cotizado(fecha_nacimiento, data.edad_inicio_trabajo)
    #tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, data.edad_jubilacion_deseada, annos_cotizados)
    anno_jubilacion = datetime.date.today().year + (data.edad_jubilacion_deseada - edad_actual)
    pension_primer_pilar = calcular_primer_pilar(data.salario_actual, annos_cotizados, data.tiene_hijos,data.n_hijos)
    return {"pension_primer_pilar": pension_primer_pilar}