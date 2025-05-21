import datetime
import logging
import warnings

import pandas as pd #type:ignore
import reflex as rx
import requests #type:ignore
from ecbdata import ecbdata as ecb  # type: ignore
    

class RatioSust1(rx.State):
    type: str = "1er Pilar"
    ratio:float = 0.0
    @rx.event
    def calcular_ratio(self, salario:float, pension:float):
        salario_valido = salario if isinstance(salario,(int,float)) else 0.0
        pension_valida = pension if isinstance(pension, (int,float)) else 0.0
        print(f"Salario: {salario}, Pension: {pension}")
        self.ratio = (pension_valida / salario_valido) * 100 if salario_valido != 0 else 0.0
        print(f"Ratio {self.type}: {self.ratio}")
        
    @rx.var
    def ratio_formateado(self) -> str:
        ratio = self.ratio if self.ratio is not None else 0.0
        return f"{ratio:.2f}%".replace('.', ',')


class RatioSust2(rx.State):
    type: str = "2o Pilar"
    ratio:float = 0.0
    @rx.event
    def calcular_ratio(self, salario:float, pension:float):
        print(f"Salario: {salario}, Pension: {pension}")
        self.ratio = float(pension / salario) * 100
        print(f"Ratio 2o Pilar: {self.ratio}")
class RatioSust3(rx.State):
    type: str = "3er Pilar"
    ratio: float = 0.0
    @rx.event
    def calcular_ratio(self, salario:float, pension:float):
        print(f"Salario: {salario}, Pension: {pension}")
        self.ratio = float(pension / salario) * 100
        print(f"Ratio 3er Pilar: {self.ratio}")

    

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Obtengo los valores del IPC desde la librería del ECB desde 1996 hasta ahora
try:
    df_cpi = ecb.get_series('ICP.M.ES.N.000000.4.ANR')[['TIME_PERIOD', 'OBS_VALUE']]
    if df_cpi.empty:
        raise ValueError(
            "Error en la obtención de los datos. Verifica la conexión o la disponibilidad de datos del IPC.")
except Exception as e:
    print(f"Error al obtener los datos del IPC: {e}")
    df_cpi = pd.DataFrame(columns=['TIME_PERIOD', 'OBS_VALUE'])  # Crear un DataFrame vacío como fallback

df_cpi['YEAR'] = pd.to_datetime(df_cpi['TIME_PERIOD']).dt.year
df_cpi['MONTH'] = pd.to_datetime(df_cpi['TIME_PERIOD']).dt.month

DF_CPI = df_cpi.drop(columns=['TIME_PERIOD'], axis=1)[['YEAR', 'MONTH', 'OBS_VALUE']].sort_values(by='YEAR',
                                                                                                  ascending=False).reset_index(
    drop=True)

# Parámetros globales según la normativa de 2024
COMPLEMENTO_MENSUAL_POR_HIJO = 36.52  # En euros, según normativa de 2024
MAX_HIJOS_APLICABLES = 4
INCREMENTO_COMPLEMENTO = 1.10
IPC_PROMEDIO_PRE_1996 = 2.5  # Asumimos un 2.5% de inflación anual antes de 1996
ANNO_ACTUAL = datetime.date.today().year
DIVISOR_BASE_REG = 350
PENSION_MINIMA = 1033.30
PENSION_MAXIMA = 3175.04

# Según datos estimados de expertos del Santander https://www.bancosantander.es/particulares/cuentas-tarjetas/cuentas-corrientes/calculadora-irpf#:~:text=Hasta%2012.450%20€%2C%20el%20tipo,tipo%20impositivo%20es%20de%2037%25.
TRAMOS_IRPF_2025 = [
    (12450.00, .19),  # Hasta 12450€: 19%
    (20200.00, .24),  # Hasta 20200€: 24%
    (35200.00, .30),  # Hasta 35200€: 30%
    (60000.00, .37),  # Hasta 60000€: 37%
    (300000.00, .45),  # Hasta 300000€: 45%
    (float('inf'), .47)  # Más de 300000€: 47%
]

# Mínimos exentos según edad (basados en normativa general de 2025)
MINIMO_EXENTO_BASE = 5550  # General
MINIMO_EXENTO_65 = 6700  # Mayores de 65 años
MINIMO_EXENTO_75 = 8100  # Mayores de 75 años


def annos_a_meses(annos: float):
    return annos * 12


# Función para calcular la edad
def calcular_edad(fecha_nacimiento):
    fecha_actual = datetime.date.today()
    edad = fecha_actual.year - fecha_nacimiento.year - (
            (fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad


# Función para estimar tiempo cotizado aprox
def estimar_tiempo_cotizado(fecha_nacimiento: datetime.date, edad_inicio_trabajo: int, edad_jubilacion_deseada: int):
    fecha_inicio_trabajo = datetime.date(fecha_nacimiento.year + int(edad_inicio_trabajo), day=15,
                                         month=6)  # Día aproximado para estimar
    # fecha_actual = datetime.date.today()
    fecha_jubilacion_deseada = datetime.date(fecha_nacimiento.year + int(edad_jubilacion_deseada), day=15, month=6)
    diff = fecha_jubilacion_deseada - fecha_inicio_trabajo
    annos_cotizados = diff.days / 365.25
    return annos_cotizados


def calcular_edad_legal_jub(fecha_nacimiento=None, edad_inicio_trabajo=None, edad_jubilacion_deseada=None,
                            annos_cotizados=None):
    if annos_cotizados is None:
        if fecha_nacimiento is None or edad_inicio_trabajo is None or edad_jubilacion_deseada is None:
            raise ValueError(
                "Deben proporcionarse fecha de nacimiento, edad de inicio de trabajo y edad de jubilacion deseada.")
        annos_cotizados = estimar_tiempo_cotizado(fecha_nacimiento, edad_inicio_trabajo, edad_jubilacion_deseada)

    if ANNO_ACTUAL >= 2027:
        return 65 if annos_cotizados >= 38.5 else 67
    elif ANNO_ACTUAL == 2024:
        return 65 if annos_cotizados >= 38 else 66.5
    elif ANNO_ACTUAL == 2025:
        return 65 if annos_cotizados >= 37.75 else 66 + (4 / 12)
    elif ANNO_ACTUAL == 2026:
        return 65 if annos_cotizados >= 38 else 66 + (10 / 12)


def estimar_bases_cotizacion(salario_actual, annos_cotizados, num_pagas=14):
    base_mensual = salario_actual / num_pagas  # Incluyendo pagas extras
    if type(annos_cotizados) == int or type(annos_cotizados) == float:
        meses_cotizados = int(annos_a_meses(annos_cotizados))
        return [base_mensual] * meses_cotizados
    else:
        print("Error: Años cotizados no válido. Introduce un número entero.")
        return


def calcular_porcentaje_por_meses(meses_cotizados):
    if meses_cotizados < 180:
        return 0
    elif meses_cotizados == 180:
        return 50
    elif meses_cotizados <= 229:  
        meses_adicionales = meses_cotizados - 180
        return 50 + (meses_adicionales * 0.21)
    elif meses_cotizados <= 438: 
        tramo1 = 49 
        tramo2 = meses_cotizados - 229
        return 50 + (tramo1 * 0.21) + (tramo2 * 0.19)
    else:
        return 100



def actualizar_base_por_ipc(base, ipc):
    if pd.isna(ipc):
        ipc = IPC_PROMEDIO_PRE_1996
    try:
        return base * (1 + ipc / 100)
    except TypeError:
        print("Error: IPC inválido, usando valor predeterminado.")
        return base * (1 + IPC_PROMEDIO_PRE_1996 / 100)


def calcular_base_reguladora(salario_anual, annos_sin_cotizar: float, tipo_trabajador, es_mujer: bool,
                             annos_a_incluir: float = 25, num_pagas=14):
    meses_a_incluir = annos_a_meses(annos_a_incluir)
    meses_sin_cotizar = round(annos_a_meses(annos_sin_cotizar))
    print("Pasados años a meses")
    bases_cotizacion = estimar_bases_cotizacion(salario_anual, annos_a_incluir, num_pagas)
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
            if mes_en_laguna < 48:  # Hasta 48 meses
                suma_bases += base_minima
            else:  # A partir del mes 49
                suma_bases += base_minima * 0.5

    # Dualidad de cálculo (a partir de 2026)
    if ANNO_ACTUAL >= 2026:
        base_reguladora = calcular_base_reguladora_dual(bases_cotizacion)
    else:
        base_reguladora = suma_bases / DIVISOR_BASE_REG

    return base_reguladora


def ajustar_pension_por_edad(pension_base, edad_deseada, edad_legal, annos_cotizados):
    """
    Ajusta la pensión según la edad de jubilación, aplicando reducciones por jubilación
    anticipada o bonificaciones por demora.
    
    Args:
        pension_base (float): Pensión mensual base ya calculada (antes de ajustes por edad).
        edad_deseada (int): Edad a la que se desea jubilar.
        edad_legal (int): Edad legal de jubilación según años cotizados.
        annos_cotizados (float): Años totales cotizados.
    
    Returns:
        float: Pensión ajustada según la edad.
    """
    meses_diferencia = (edad_deseada - edad_legal) * 12
    if meses_diferencia > 0:  # Demora
        pension_con_bonus = calcular_bonificacion_demora(pension_base, meses_diferencia)
        pension_ajustada = pension_base + pension_con_bonus
    elif meses_diferencia < 0:  # Anticipación
        coef_reductor = calcular_coeficiente_reductor(meses_diferencia, annos_cotizados)
        pension_ajustada = pension_base * (1 - coef_reductor)
    else:  # Exactamente la edad legal
        pension_ajustada = pension_base
    return pension_ajustada


def calcular_coeficiente_reductor(meses_anticipacion, annos_cotizados):
    meses_anticipacion = abs(meses_anticipacion)  # Convertir a positivo
    if meses_anticipacion > 24:
        raise ValueError("No se permite anticipar más de 24 meses voluntariamente.")
    if annos_cotizados < 38:
        coef_reductor = meses_anticipacion * 0.005  # 0.5% por mes
    else:
        coef_reductor = meses_anticipacion * 0.004  # 0.4% por mes
    return coef_reductor


def calcular_bonificacion_demora(pension_base: float, meses_demora: int):
    """
    Calcula la bonificación por demora de la jubilación según las tres opciones disponibles:
    1. Porcentaje adicional sobre la pensión
    2. Cantidad a tanto alzado
    3. Opción mixta
    
    Args:
        pension_base (float): Pensión mensual base
        meses_demora (int): Número de meses de demora en la jubilación
    
    Returns:
        float: La mejor bonificación mensual entre las tres opciones
    """
    # Calcular el porcentaje adicional: 4% por cada año completo de demora
    annos_demora = meses_demora // 12  # Solo años completos
    bonus_porcentaje = pension_base * (annos_demora * 0.04)
    return bonus_porcentaje


def calcular_base_reguladora_dual(bases_cotizacion):
    if len(bases_cotizacion) < 29 * 12:
        raise ValueError("No hay suficientes datos para calcular los 29 años de bases cotización.")
    base_25 = sum(bases_cotizacion[-25:]) / DIVISOR_BASE_REG
    bases_mejoradas = sorted(bases_cotizacion[:-2], reverse=True)[:27]
    base_29 = sum(bases_mejoradas) / DIVISOR_BASE_REG
    return max(base_25, base_29)


def obtener_base_minima(anno, mes_en_laguna, tipo_trabajador):
    # Definir bases minimas de 2024 según tipo de trabajador
    if tipo_trabajador == "general":
        base_minima_2024 = 1323
    else:
        base_minima_2024 = 960.78

    if anno == ANNO_ACTUAL:
        return base_minima_2024
    else:
        ipc = DF_CPI[(DF_CPI['YEAR'] == anno) & (DF_CPI['MONTH'] == mes_en_laguna)]['OBS_VALUE'].iloc[0] if not DF_CPI[
            (DF_CPI['YEAR'] == anno) & (DF_CPI['MONTH'] == mes_en_laguna)].empty else IPC_PROMEDIO_PRE_1996
        return base_minima_2024 * (1 + ipc / 100)  # Actualizar la base mínima por IPC


def calcular_complemento_brecha_genero(num_hijos):
    if num_hijos == "4+":
        num_hijos = MAX_HIJOS_APLICABLES
    else:
        num_hijos = int(num_hijos)
    complemento_base = num_hijos * COMPLEMENTO_MENSUAL_POR_HIJO
    complemento_total = complemento_base * INCREMENTO_COMPLEMENTO
    return complemento_total if num_hijos > 0 else 0


def calcular_irpf(pension_bruta_anual, edad_pensionista):
    """Calcula el impuesto IRPF anual aplicado a la pensión bruta, considerando tramos de renta y el mínimo exento según la edad del pensionista.

    Args:
        pension_bruta_anual (float): Pensión bruta anual a la que aplicar el IRPF.
        edad_pensionista (int): Edad del pensionista al jubilarse
    Returns:
        float: Impuesto IRPF anual aplicado a la pensión bruta.
    """

    if edad_pensionista >= 75:
        minimo_exento = MINIMO_EXENTO_75
    elif edad_pensionista >= 65:
        minimo_exento = MINIMO_EXENTO_65
    else:
        minimo_exento = MINIMO_EXENTO_BASE

    base_imponible = max(0, pension_bruta_anual - minimo_exento)

    # Calcular el impuesto según tramos
    impuesto = 0
    base_restante = base_imponible
    limite_anterior = 0
    for limite, tasa in TRAMOS_IRPF_2025:
        if base_restante <= 0:
            break
        tramo_gravable = min(base_restante, limite - limite_anterior)
        impuesto += tramo_gravable * tasa
        base_restante -= tramo_gravable
        limite_anterior = limite

    return impuesto


def calcular_primer_pilar(base_reguladora, annos_cotizados, tiene_hijos, num_hijos, edad_deseada):
    """Calcula la pensión bruta mensual del primer pilar, considerando el porcentaje por años cotizados,
    ajustes por edad de jubilación (anticipada o demorada) y el complemento por brecha de género.
    Args:
        base_reguladora (float): Base reguladora calculada.
        annos_cotizados (float): Años cotizados.
        tiene_hijos (str): 'sí' o 'no' para complementar por brecha de género.
        num_hijos (str/int): Número de hijos o '4+'.
        edad_deseada (int): Edad a la que se desea jubilar.

    Returns:
        float: Pensión bruta mensual ajustada.
    """
    if base_reguladora < 0 or annos_cotizados < 0 or edad_deseada < 0:
        raise ValueError("Base reguladora, años cotizados y edad deseada deben ser positivos.")
    diferencia_annos_porcentaje = 36.5 - 15
    meses_cotizados = annos_cotizados * 12
    porcentaje = calcular_porcentaje_por_meses(meses_cotizados)

    # Calcular la pensión base antes de ajustes por edad
    pension_base = base_reguladora * (porcentaje / 100)  # Pensión mensual sin ajustes

    # Cálculo de edad legal de jubilación
    edad_legal = calcular_edad_legal_jub(annos_cotizados = annos_cotizados)

    # Ajustar la pensión según la edad de jubilación (anticipada o demorada)
    pension_ajustada = ajustar_pension_por_edad(pension_base, edad_deseada, edad_legal, annos_cotizados)

    # Aplicar el complemento por brecha de género si tiene hijos, después del ajuste por edad
    if tiene_hijos.lower().startswith("s"):
        complemento = calcular_complemento_brecha_genero(num_hijos)
        pension_ajustada += complemento

    # Verificar si la pensión supera los límites de pensión mínima o máxima. En caso de que la pension_ajustada sea 0, será porque el usuario no está en la edad legal para jubilarse.
    pension_bruta_mensual = max(PENSION_MINIMA,
                                min(pension_ajustada, PENSION_MAXIMA)) if pension_ajustada != 0 else pension_ajustada

    return pension_bruta_mensual



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


def calcular_pension_segundo_pilar(aportacion_empleador, aportacion_empleado_voluntaria, salario_anual,
                                   periodo_aportacion_annos: int, edad_jubilacion, rentabilidad_anual_esperada):
    """
    Calcula una estimación de la pensión mensual del SEGUNDO PILAR
    (previsión social empresarial) separando la aportación del empleador y la aportación voluntaria del empleado,
    considerando las aportaciones periódicas, la rentabilidad esperada, el factor actuarial (esperanza de vida)
    y otros factores simplificados.

    Args:
        aportacion_empleador (float): Porcentaje del salario anual aportado periódicamente por el empleador (por ejemplo, 5%).
        aportacion_empleado_voluntaria (float): Porcentaje del salario anual aportado voluntariamente por el empleado (e.g., 2.0 para 2%).
        salario_anual (float): Salario anual del empleado.
        periodo_aportacion_annos (int): Número de años durante los que se realizan las aportaciones.
        rentabilidad_anual_esperada (float): Rentabilidad anual esperada de las inversiones (en decimal, e.g., 0.05 para 5%).
        edad_jubilacion (int): Edad de jubilación deseada del empleado.
    Returns:
        float: Estimación muy simplificada de la pensión anual del segundo pilar.
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


def calcular_pension_tercer_pilar(aportacion_periodica, periodo_aportacion_annos, rentabilidad_anual_esperada,
                                  edad_jubilacion):
    """Calcula una estimación MUY SIMPLIFICADA de la pensión anual del TERCER PILAR
    (ahorro individual para la jubilación) considerando las aportaciones periódicas,
    la rentabilidad esperada, el factor actuarial (esperanza de vida) y otros factores simplificados.

    Esta función esta basada en meras aproximaciones, hay más variables en el cálculo real.

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
        rendimiento = capital_acumulado * rentabilidad_anual_esperada  # Calcular rendimiento
        capital_acumulado += rendimiento  # Añadir rendimiento al capital

    pension_3p = capital_acumulado / esperanza_vida_jubilacion

    return pension_3p / 12


def calcular_pension_bruta_total(pension_bruta_mensual_1p: float, pension_bruta_mensual_2p: float,
                                 pension_bruta_mensual_3p: float) -> float:
    """Calcular la pensión total, antes de impuestos.
    Args:
        pension_bruta_mensual_1p (float): Pensión pública
        pension_bruta_mensual_2p (float): Pensión de empresa
        pension_bruta_mensual_3p (float): Pensión privada
    Returns:
        float: Pensión total antes de IRPF.
    """
    return pension_bruta_mensual_1p + pension_bruta_mensual_2p + pension_bruta_mensual_3p


def calcular_pension_neta_total(pension_bruta_mensual_1p: float, pension_bruta_mensual_2p: float,
                                pension_bruta_mensual_3p: float,
                                edad_jubilacion_deseada: int) -> float:
    """Calcular la pensión total teniendo en cuenta el IRPF anual.
    Args:
        pension_bruta_mensual_1p (float): Pensión pública antes de IRPF.
        pension_bruta_mensual_2p (float): Pensión de empresa antes de IRPF.
        pension_bruta_mensual_3p (float): Pensión privada antes de IRPF.
        edad_jubilacion_deseada (int): Edad de jubilación deseada por el usuario
    Returns:
        float: Pensión total después de IRPF.
    """
    total_bruto_mensual = calcular_pension_bruta_total(pension_bruta_mensual_1p, pension_bruta_mensual_2p,
                                                       pension_bruta_mensual_3p)
    total_bruto_anual = total_bruto_mensual * 12
    irpf_anual = calcular_irpf(total_bruto_anual, edad_jubilacion_deseada)
    ingreso_neto_anual = total_bruto_anual - irpf_anual
    return ingreso_neto_anual / 12
