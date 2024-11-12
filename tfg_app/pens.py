import pandas as pd
from ecbdata import ecbdata as ecb # type: ignore
import datetime
from dateutil import parser

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

# Parámetros globales
COMPLEMENTO_MENSUAL_POR_HIJO = 33.20  # En euros, según normativa de 2024
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
def estimar_tiempo_cotizado(fecha_nacimiento, edad_inicio_trabajo):
    fecha_nacimiento = parser.parse(input("Fecha de nacimiento (dd/mm/YYYY): ")).date()
    edad_inicio_trabajo = validar_entrada_numerica("Edad al comenzar a cotizar: ")
    fecha_inicio_trabajo = datetime.date(fecha_nacimiento.year + int(edad_inicio_trabajo), 15, 6)  # Día aproximado para estimar
    fecha_actual = datetime.date.today()
    diff = fecha_actual - fecha_inicio_trabajo
    annos_cotizados = diff.days / 365.25
    return annos_cotizados, fecha_nacimiento

def calcular_edad_legal_jub():
    annos_cotizados, fecha_nacimiento = estimar_tiempo_cotizado()
    if annos_cotizados < 38:
        return 66.5, fecha_nacimiento
    else:
        return 65, fecha_nacimiento

def estimar_bases_cotizacion(annos_cotizados, num_pagas=14):
    salario_actual = validar_entrada_numerica("Introduce tu salario bruto anual actual: ")
    base_mensual = salario_actual / num_pagas  # Incluyendo pagas extras
    meses_cotizados = int(annos_a_meses(annos_cotizados))
    return [base_mensual] * meses_cotizados

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
    return base * (1 + ipc / 100)

def calcular_base_reguladora(salario_anual, annos_a_incluir=25, num_pagas=14):
    meses_a_incluir = annos_a_meses(annos_a_incluir)
    bases_cotizacion = estimar_bases_cotizacion(annos_a_incluir, num_pagas)
    bases_actualizadas = []
    for i in range(len(bases_cotizacion)):
        if i < 24:
            bases_actualizadas.append(bases_cotizacion[-(i + 1)])  # Los últimos 24 meses sin actualizar por IPC
        else:
            base = bases_cotizacion[i]
            ipc = DF_CPI.iloc[i]['OBS_VALUE']
            base_actualizada = actualizar_base_por_ipc(base, ipc)
            bases_actualizadas.append(base_actualizada)

    suma_bases = sum(bases_actualizadas[:meses_a_incluir])
    base_reguladora = suma_bases / DIVISOR_BASE_REG
    return base_reguladora

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
    pension_primer_pilar = base_reguladora * (porcentaje / 100)

        # Verificar si la pensión supera los límites de pensión mínima o máxima
    pension_primer_pilar = max(PENSION_MINIMA, min(pension_primer_pilar, PENSION_MAXIMA))

    # Aplicar el complemento por brecha de género si tiene hijos
    if tiene_hijos.lower() == "sí":
        complemento = calcular_complemento_brecha_genero(num_hijos)
        pension_primer_pilar += complemento



    return pension_primer_pilar

def obtener_datos_segundo_pilar_usuario(salario_actual, categoria, ppe_porcentaje_empresa=5, aportacion_voluntaria_ppe=0, aportacion_excesos_empresa=0, aportacion_excesos_voluntaria=0, derechos_consolidados=1000, provisiones_matematicas=500):
    """
    Calcula las aportaciones al segundo pilar (PPE, Excesos, Flex) según la categoría del usuario y sus aportaciones existentes.
    
    Args:
    - salario_actual: Salario anual bruto del usuario.
    - categoria: La categoría del usuario (1-5).
    - ppe_porcentaje_empresa: Porcentaje que la empresa aporta al PPE.
    - aportacion_voluntaria_ppe: Aportación voluntaria del empleado al PPE.
    - aportacion_excesos_empresa: Aportación de la empresa al plan de Excesos.
    - aportacion_excesos_voluntaria: Aportación voluntaria del empleado al plan de Excesos.
    - derechos_consolidados: Derechos ya acumulados hasta la fecha (PPE y Excesos).
    - provisiones_matematicas: Provisiones matemáticas ya calculadas.
    
    Returns:
    - total_segundo_pilar: Contribución total del segundo pilar con derechos y provisiones.
    """
    
    print("\n--- Calculando las Aportaciones al Segundo Pilar según categoría ---")
    
    # Aportación de la empresa al PPE
    if categoria in [1, 2, 3]:  # Categorías con PPE y Excesos
        aportacion_empresa_ppe = salario_actual * (ppe_porcentaje_empresa / 100)
    else:
        aportacion_empresa_ppe = 0  # Categorías sin acceso a PPE
    
    # Aportaciones voluntarias y de excesos
    if categoria in [1, 2, 3]:  # Excesos y flexibilidad solo en algunas categorías
        total_excesos = aportacion_excesos_empresa + aportacion_excesos_voluntaria
    else:
        total_excesos = 0
    
    total_ppe = aportacion_empresa_ppe + aportacion_voluntaria_ppe
    
    # Mostrar resumen de aportaciones
    print(f"Aportación de la empresa al PPE: {aportacion_empresa_ppe:.2f} €")
    print(f"Aportación voluntaria al PPE: {aportacion_voluntaria_ppe:.2f} €")
    print(f"Total aportación al PPE: {total_ppe:.2f} €")
    print(f"Aportación total al plan de Excesos: {total_excesos:.2f} €")
    
    # Total segundo pilar incluyendo derechos consolidados y provisiones
    total_segundo_pilar = total_ppe + total_excesos + derechos_consolidados + provisiones_matematicas
    print(f"Derechos consolidados: {derechos_consolidados:.2f} €")
    print(f"Provisiones matemáticas: {provisiones_matematicas:.2f} €")
    print(f"Total aportaciones al segundo pilar (con derechos y provisiones): {total_segundo_pilar:.2f} €")
    
    return total_segundo_pilar

# Función para calcular el ratio de sustitución de ingresos del segundo pilar
def calcular_ratio_sustitucion(segundo_pilar_total, salario_pensionable):
    ratio_sustitucion = (segundo_pilar_total / salario_pensionable) * 100
    print(f"Ratio de sustitución del Pilar II: {ratio_sustitucion:.2f}%")
    return ratio_sustitucion



    
