import os
import pandas as pd
from ecbdata import ecbdata as ecb # type: ignore
import datetime
import reflex as rx
import math 
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import warnings
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')



# Obtengo los valores del IPC desde la librería del ECB desde 1996 hasta ahora
try:
    df_cpi = ecb.get_series('ICP.M.ES.N.000000.4.ANR')[['TIME_PERIOD','OBS_VALUE']]
    if df_cpi.empty:
        raise ValueError("Error en la obtención de los datos. Verifica la conexión o la disponibilidad de datos del IPC.")
except Exception as e:
    print(f"Error al obtener los datos del IPC: {e}")
    df_cpi = pd.DataFrame(columns=['TIME_PERIOD', 'OBS_VALUE'])  # Crear un DataFrame vacío como fallback

df_cpi['YEAR'] = pd.to_datetime(df_cpi['TIME_PERIOD']).dt.year
df_cpi['MONTH'] = pd.to_datetime(df_cpi['TIME_PERIOD']).dt.month

DF_CPI = df_cpi.drop(columns=['TIME_PERIOD'], axis=1)[['YEAR', 'MONTH', 'OBS_VALUE']].sort_values(by='YEAR', ascending=False).reset_index(drop=True)

# Parámetros globales según la normativa de 2024
COMPLEMENTO_MENSUAL_POR_HIJO = 36.52  # En euros, según normativa de 2024
MAX_HIJOS_APLICABLES = 4
INCREMENTO_COMPLEMENTO = 1.10
IPC_PROMEDIO_PRE_1996 = 2.5  # Asumimos un 2.5% de inflación anual antes de 1996
ANNO_ACTUAL = datetime.date.today().year
DIVISOR_BASE_REG = 350
PENSION_MINIMA = 1033.30
PENSION_MAXIMA = 3175.04

def annos_a_meses(annos):
    return annos * 12
# Función para validar que el input es un valor numérico
def validar_entrada_numerica(mensaje, valor_minimo=None, valor_maximo=None):
    while True:
        try:
            valor = float(input(mensaje))
            if valor_minimo is not None and valor < valor_minimo:
                print(f"El valor debe ser mayor o igual a {valor_minimo}. Inténtalo de nuevo.")
            elif valor_maximo is not None and valor > valor_maximo:
                print(f"El valor debe ser menor o igual a {valor_maximo}. Inténtalo de nuevo.")
            else:
                return valor
        except ValueError:
            print("Entrada inválida. Por favor, introduce un número.")

# Función para calcular la edad
def calcular_edad(fecha_nacimiento):
    fecha_actual = datetime.date.today()
    edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

# Función para estimar tiempo cotizado aprox
def estimar_tiempo_cotizado(fecha_nacimiento:datetime.date, edad_inicio_trabajo:int,edad_jubilacion_deseada:int):
    fecha_inicio_trabajo = datetime.date(fecha_nacimiento.year + int(edad_inicio_trabajo), day=15, month=6)  # Día aproximado para estimar
    #fecha_actual = datetime.date.today()
    fecha_jubilacion_deseada = datetime.date(fecha_nacimiento.year + int(edad_jubilacion_deseada), day=15, month=6)
    diff = fecha_jubilacion_deseada - fecha_inicio_trabajo
    annos_cotizados = diff.days / 365.25
    return annos_cotizados

def calcular_edad_legal_jub(fecha_nacimiento:datetime.date,edad_inicio_trabajo:int):
    annos_cotizados = estimar_tiempo_cotizado(fecha_nacimiento,edad_inicio_trabajo)

    if ANNO_ACTUAL >= 2027:
        return 65 if annos_cotizados >= 38.5 else 67
    elif ANNO_ACTUAL == 2024:
        return 65 if annos_cotizados >= 38 else 66.5
    elif ANNO_ACTUAL == 2025:
        return 65 if annos_cotizados >= 38 else 66.75
    elif ANNO_ACTUAL == 2026:
        return 65 if annos_cotizados >= 38 else 66 + (10 / 12)

def estimar_bases_cotizacion(salario_actual,annos_cotizados, num_pagas=14):
    base_mensual = salario_actual / num_pagas  # Incluyendo pagas extras
    annos_cotizados = validar_entrada_numerica(annos_cotizados, 0)
    if type(annos_cotizados) == int:
        meses_cotizados = int(annos_a_meses(validar_entrada_numerica(annos_cotizados,0)))
        return [base_mensual] * meses_cotizados
    else:
        print("Error: Años cotizados no válido. Introduce un número entero.")
        return

def calcular_porcentaje_por_meses(months_cotizados):
    if months_cotizados < 180:  # 15 años (180 meses)
        return 0
    elif months_cotizados == 180:
        return 50  # 50% si ha cotizado exactamente 15 años (180 meses)
    elif months_cotizados <= 300:  # Entre 15 y 25 años (180-300 meses)
        return 50 + (months_cotizados - 180) * (1.5 / 12)
    elif months_cotizados > 300 and months_cotizados <= 444:  # Entre 25 y 37 años (300-444 meses)
        return 80 + (months_cotizados - 300) * (1.5 / 12)
    else:
        return 100  # Máximo del 100% si ha cotizado más de 444 meses (37 años)

def actualizar_base_por_ipc(base, ipc):
    if pd.isna(ipc):
        ipc = IPC_PROMEDIO_PRE_1996
    try:
        return base * (1 + ipc / 100)
    except TypeError:
        print("Error: IPC inválido, usando valor predeterminado.")
        return base * (1 + IPC_PROMEDIO_PRE_1996 / 100)


def calcular_base_reguladora(salario_anual, annos_sin_cotizar, tipo_trabajador, es_mujer: bool, annos_a_incluir=25, num_pagas=14):
    meses_a_incluir = annos_a_meses(annos_a_incluir)
    meses_sin_cotizar = annos_a_meses(annos_sin_cotizar)
    bases_cotizacion = estimar_bases_cotizacion(salario_anual,annos_a_incluir, num_pagas)
    bases_actualizadas = []

    for i, base in enumerate(bases_cotizacion):
        if i < 24:
            bases_actualizadas.append(bases_cotizacion[-(i + 1)])
        else:
            ipc = DF_CPI['OBS_VALUE'].iloc[i] if i < len(DF_CPI) else IPC_PROMEDIO_PRE_1996
            bases_actualizadas.append(actualizar_base_por_ipc(base, ipc))


    suma_bases = sum(bases_actualizadas[:meses_a_incluir])

    # Gestión de lagunas de cotización
    for mes_en_laguna in range(meses_sin_cotizar):
        base_minima = obtener_base_minima(ANNO_ACTUAL, mes_en_laguna, tipo_trabajador)
        if tipo_trabajador == "general":
            if es_mujer:
                if mes_en_laguna < 60:
                    factor = 1
                elif mes_en_laguna < 84:
                    factor = 0.8
                else:
                    factor = 0.5
            else:
                if mes_en_laguna < 48:
                    factor = 1
                else:
                    factor = 0.5
            suma_bases += base_minima * factor
        elif tipo_trabajador == "autonomo":
            if mes_en_laguna < 6:
                suma_bases += base_minima


    # Dualidad de cálculo (a partir de 2026)
    if ANNO_ACTUAL >= 2026:
        base_reguladora = calcular_base_reguladora_dual(bases_cotizacion)
    else:
        base_reguladora = suma_bases / DIVISOR_BASE_REG

    # Aplicar límites
    base_reguladora = max(PENSION_MINIMA, min(base_reguladora, PENSION_MAXIMA))

    return base_reguladora


def ajustar_pension_por_edad(base_reguladora,edad_deseada, edad_legal, annos_cotizados):
    meses_diferencia = (edad_deseada - edad_legal) * 12
    if meses_diferencia < 0: # Jubilación anticipada
        coef_reductor = calcular_coeficiente_reductor(-meses_diferencia,annos_cotizados)
        return base_reguladora * (1 - coef_reductor)
    elif meses_diferencia > 0: # Jubilación prolongada
        incentivo = calcular_incentivo(meses_diferencia)
        return base_reguladora * (1 + incentivo)
    return base_reguladora

def calcular_coeficiente_reductor(meses_anticipados, annos_cotizados):
    if annos_cotizados < 38:
        return meses_anticipados * 0.005  # Ejemplo: 0.5% por mes
    else:
        return meses_anticipados * 0.004  # 0.4% por mes para cotizaciones altas

def calcular_incentivo(meses_demora):
    return meses_demora * 0.006  # Ejemplo: 0.6% por mes adicional

def calcular_base_reguladora_dual(bases_cotizacion):
    if len(bases_cotizacion) < 29 * 12:
        raise ValueError("No hay suficientes datos para calcular los 29 años de bases cotización.")
    base_25 = sum(bases_cotizacion[-25:]) / DIVISOR_BASE_REG
    bases_mejoradas = sorted(bases_cotizacion[:-2], reverse=True)[:27]
    base_29 = sum(bases_mejoradas) / DIVISOR_BASE_REG
    return max(base_25, base_29)


def agregar_bases_pluriactividad(bases_regimenes, base_maxima):
    total_base = sum(bases_regimenes)
    return min(total_base, base_maxima)




def obtener_base_minima(anno, mes_en_laguna, tipo_trabajador):

    # Definir bases minimas de 2024 según tipo de trabajador
    if tipo_trabajador == "general":
        base_minima_2024 = 1323
    else:
        base_minima_2024 = 960.78
    
    if anno == ANNO_ACTUAL:
        return base_minima_2024
    else:
        ipc = DF_CPI[(DF_CPI['YEAR'] == anno) & (DF_CPI['MONTH'] == mes_en_laguna)]['OBS_VALUE'].iloc[0] if not DF_CPI[(DF_CPI['YEAR'] == anno) & (DF_CPI['MONTH'] == mes_en_laguna)].empty else IPC_PROMEDIO_PRE_1996
        return base_minima_2024 * (1 + ipc / 100) # Actualizar la base mínima por IPC

def calcular_complemento_brecha_genero(num_hijos):
    if num_hijos == "4+":
        num_hijos = MAX_HIJOS_APLICABLES
    else:
        num_hijos = int(num_hijos)
    complemento_base = num_hijos * COMPLEMENTO_MENSUAL_POR_HIJO
    complemento_total = complemento_base * INCREMENTO_COMPLEMENTO
    return complemento_total if num_hijos > 0 else 0

def calcular_primer_pilar(base_reguladora, annos_cotizados, tiene_hijos, num_hijos):
    if annos_cotizados < 15:
        return 0  # No tiene derecho a pensión si no ha cotizado al menos 15 años
    elif annos_cotizados == 15:
        porcentaje = 50  # 50% de la base reguladora
    elif annos_cotizados < 36.5:
        porcentaje = 50 + (annos_cotizados - 15) * 1.5  # 1.5% adicional por año entre 15 y 36.5
    else:
        porcentaje = 100  # A partir de 36 años y medio, se tiene derecho al 100%

    # Calcular la pensión base
    pension_primer_pilar = base_reguladora * (porcentaje / 100) / 12  # Pensión mensual
    

       

    # Aplicar el complemento por brecha de género si tiene hijos
    if tiene_hijos.lower().startswith("s"):
        complemento = calcular_complemento_brecha_genero(num_hijos) 
        pension_primer_pilar += complemento

     # Verificar si la pensión supera los límites de pensión mínima o máxima
    pension_primer_pilar = max(PENSION_MINIMA, min(pension_primer_pilar, PENSION_MAXIMA))

    return pension_primer_pilar

def calcular_ratio_sustitucion(pension_primer_pilar:rx.Var, salario_actual:rx.Var) -> float:
    r_s = (pension_primer_pilar *12 / salario_actual) * 100
    return (math.ceil(r_s*100)/100).to(float) #Resultado redondeado

def obtener_esperanza_vida_jub(edad_jubilacion):
    """Obtener la esperanza de vida restante en años desde la edad de jubilación.
    Args:
        edad_jubilacion (int): Edad de jubilación en años.
    Returns:
        int: Esperanza de vida restante en años desde la edad de jubilación.
    """
    try:
        # Obtención de la esperanza de vida (valor aproximado) usando la API del Banco Mundial
        url = "http://api.worldbank.org/v2/country/ESP/indicator/SP.DYN.LE00.IN?format=json&per_page=5"
        response = requests.get(url)
        data = response.json()[1]
        # Se recorre para obtener el primer valor disponible (valor reciente)
        esperanza_vida = None
        for registro in data:
            if registro['value'] is not None:
                esperanza_vida = round(registro['value'], 2)
                break
        if esperanza_vida is None:
            raise ValueError("No se encontró valor válido de esperanza de vida.")
    except Exception as e:
        print(f"Error al obtener los datos de esperanza de vida: {e}")
        esperanza_vida = 83  # Valor por defecto en caso de error

    print(f"Esperanza de vida: {esperanza_vida} años")

    return int(esperanza_vida - edad_jubilacion)


   





def calcular_pension_segundo_pilar(aportacion_empleador, aportacion_empleado_voluntaria, categoria, salario_anual, periodo_aportacion_annos:int, edad_jubilacion, rentabilidad_anual_esperada):
    """
    Calcula una estimación MUY SIMPLIFICADA de la pensión mensual del SEGUNDO PILAR
    (previsión social empresarial) separando la aportación del empleador y la aportación voluntaria del empleado,
    considerando las aportaciones periódicas, la rentabilidad esperada, el factor actuarial (esperanza de vida)
    y otros factores simplificados.

    Args:
        aportacion_empleador (float): Porcentaje del salario anual aportado periódicamente por el empleador (por ejemplo, 5%).
        aportacion_empleado_voluntaria (float): Porcentaje del salario anual aportado voluntariamente por el empleado (e.g., 2.0 para 2%).
        salario_anual (float): Salario anual del empleado.
        periodo_aportacion_anios (int): Número de años durante los que se realizan las aportaciones.
        rentabilidad_anual_esperada (float): Rentabilidad anual esperada de las inversiones (en decimal, e.g., 0.05 para 5%).
        edad_jubilacion (int): Edad de jubilación deseada del empleado.
    Returns:
        float: Estimación MUY SIMPLIFICADA de la pensión anual del segundo pilar.
    """

    esperanza_vida_jubilacion = obtener_esperanza_vida_jub(edad_jubilacion)
    if esperanza_vida_jubilacion <= 0:
        return 0
    print("Esperanza de vida de jubilación: ", esperanza_vida_jubilacion)
    capital_acumulado = 0
    for _ in range(int(periodo_aportacion_annos)):
        aportacion_anual_empleador = salario_anual * (aportacion_empleador / 100)
        aportacion_anual_empleado = salario_anual * (aportacion_empleado_voluntaria / 100)
        aportacion_total_anual = aportacion_anual_empleador + aportacion_anual_empleado

        capital_acumulado += aportacion_total_anual  # Realizar aportación total (empleador + empleado)
        rendimiento = capital_acumulado * rentabilidad_anual_esperada  # Calcular rendimiento
        capital_acumulado += rendimiento  # Añadir rendimiento al capital
    print("Capital acumulado: ", capital_acumulado)
    pension_2p = capital_acumulado / esperanza_vida_jubilacion
    
    return pension_2p / 12


def calcular_pension_tercer_pilar(aportacion_periodica, periodo_aportacion_annos, rentabilidad_anual_esperada, edad_jubilacion):
    """
    Calcula una estimación MUY SIMPLIFICADA de la pensión anual del TERCER PILAR
    (ahorro individual para la jubilación) considerando las aportaciones periódicas,
    la rentabilidad esperada, el factor actuarial (esperanza de vida) y otros factores simplificados.

    ESTA FUNCIÓN ES SOLO PARA FINES ILUSTRATIVOS Y NO REFLEJA LA COMPLEJIDAD
    DE LOS CÁLCULOS REALES DE PENSIONES.

    Args:
        aportacion_periodica (float): Cantidad aportada periódicamente (e.g., anual).
        periodo_aportacion_annos (int): Número de años durante los que se realizan las aportaciones.
        rentabilidad_anual_esperada (float): Rentabilidad anual esperada de las inversiones (en decimal, e.g., 0.05 para 5%).
        edad_jubilacion (int): Edad de jubilación deseada del empleado.
        
    Returns:
        float: Estimación MUY SIMPLIFICADA de la pensión anual del tercer pilar.
    """
    esperanza_vida_jubilacion = obtener_esperanza_vida_jub(edad_jubilacion)
    if esperanza_vida_jubilacion <= 0:
        return 0

    capital_acumulado = 0
    for _ in range(int(periodo_aportacion_annos)):
        capital_acumulado += aportacion_periodica  # Realizar aportación
        rendimiento = capital_acumulado * rentabilidad_anual_esperada # Calcular rendimiento
        capital_acumulado += rendimiento # Añadir rendimiento al capital


    pension_3p = capital_acumulado / esperanza_vida_jubilacion
   

    return pension_3p/12



"""
def calcular_tercer_pilar(capital_inicial, rentabilidad_esperada, aportacion_anual, annos, edad_jubilacion, tasa_conversion=3) -> float:
    """
"""
Calcula la pensión mensual del tercer pilar (ahorro individual) a partir del capital inicial,
las aportaciones anuales y la rentabilidad esperada.

La acumulación se realiza con la rentabilidad esperada, pero la conversión a anualidad utiliza 
una tasa de conversión (tasa_conversion) que suele ser más conservadora.
"""
"""
    # Acumular el capital usando interés compuesto y aportaciones anuales
    capital_final = (capital_inicial * (1 + rentabilidad_esperada / 100) ** annos +
                     aportacion_anual * (((1 + rentabilidad_esperada / 100) ** annos - 1) / (rentabilidad_esperada / 100)))
    # Obtener el factor actuarial basado en la tasa_conversion y la edad de jubilación
    factor_actuarial = calcular_factor_actuarial(tasa_conversion, edad_jubilacion)
    # La pensión mensual es el capital final dividido por el factor actuarial
    pension_mensual = capital_final / factor_actuarial
    return pension_mensual
"""