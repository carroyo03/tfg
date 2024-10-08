import datetime
from ecbdata import ecbdata as ecb
import pandas as pd

# Obtener la serie de datos del IPC
try:
    df_cpi = ecb.get_series('ICP.M.ES.N.000000.4.ANR')[['TIME_PERIOD', 'OBS_VALUE']]
    if df_cpi.empty:
        raise ValueError("La serie de datos está vacía. Verifica la conexión o la disponibilidad de datos del IPC.")
except Exception as e:
    print(f"Error al obtener los datos del IPC: {e}")
    df_cpi = pd.DataFrame(columns=['TIME_PERIOD', 'OBS_VALUE'])  # Crear un DataFrame vacío como fallback

df_cpi['YEAR'] = pd.to_datetime(df_cpi['TIME_PERIOD']).dt.year
df_annual_cpi = df_cpi.groupby('YEAR').mean('OBS_VALUE').reset_index()

# Función para calcular la edad
def calcular_edad(fecha_nacimiento):
    fecha_actual = datetime.date.today()
    edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

# Función para calcular tiempo cotizado simplificado
def estimar_tiempo_cotizado_simplificado():
    # Fecha de nacimiento
    dia_nacimiento = int(input("Introduce el día de nacimiento: "))
    mes_nacimiento = int(input("Introduce el mes de nacimiento: "))
    anno_nacimiento = int(input("Introduce el año de nacimiento: "))
    fecha_nacimiento = datetime.date(anno_nacimiento, mes_nacimiento, dia_nacimiento)
    
    # Edad aproximada en que comenzó a trabajar
    edad_inicio_trabajo = int(input("¿A qué edad comenzaste a trabajar aproximadamente?: "))
    
    # Solicitar si el usuario recuerda el mes y día aproximado en que comenzó a trabajar
    recordar_fecha_trabajo = input("¿Recuerdas el mes y día aproximado en el que comenzaste a trabajar? (si/no): ").strip().lower()
    if recordar_fecha_trabajo == 'si':
        mes_inicio_trabajo = int(input("Introduce el mes aproximado en el que comenzaste a trabajar: "))
        dia_inicio_trabajo = int(input("Introduce el día aproximado en el que comenzaste a trabajar: "))
    else:
        # Usar un valor predeterminado de mediados de año si no se recuerda
        mes_inicio_trabajo = 6  # Junio, mitad de año
        dia_inicio_trabajo = 15  # Día en la mitad del mes
    
    # Calcular fecha de inicio de trabajo aproximada
    fecha_inicio_trabajo = datetime.date(anno_nacimiento + edad_inicio_trabajo, mes_inicio_trabajo, dia_inicio_trabajo)
    
    # Fecha actual
    fecha_actual = datetime.date.today()
    
    # Calcular años y meses cotizados
    delta = fecha_actual - fecha_inicio_trabajo
    annos_cotizados = delta.days // 365  # Convertir días a años
    meses_cotizados = (delta.days % 365) // 30  # Convertir el resto de días en meses aproximadamente

    return annos_cotizados, meses_cotizados, fecha_nacimiento

# Función para calcular si es anticipación o demora en la jubilación
def calcular_annos_anticipacion_o_demora(edad_actual, edad_jubilacion_deseada, annos_cotizados):
    # Edad ordinaria de jubilación según los años cotizados
    if annos_cotizados >= 38.5:
        edad_ordinaria = 65
    else:
        edad_ordinaria = 66.5
    
    if edad_jubilacion_deseada < edad_ordinaria:
        # Caso de jubilación anticipada
        return "anticipacion", int((edad_ordinaria - edad_jubilacion_deseada) * 12)
    elif edad_jubilacion_deseada > edad_ordinaria:
        # Caso de jubilación demorada
        return "demora", int((edad_jubilacion_deseada - edad_ordinaria) * 12)
    else:
        # Jubilación ordinaria
        return "ordinaria", 0

# Función para estimar las bases de cotización ajustadas
def estimar_bases_cotizacion(salario_actual, annos_cotizados, meses_cotizados, df_annual_cpi):
    bases_cotizacion = []
    ipc_ordenado = df_annual_cpi.sort_values(by='YEAR', ascending=True)

    # Definir un IPC promedio para los años anteriores a 1996
    ipc_promedio_pre_1996 = 2.5  # Asumimos un 2.5% de inflación anual antes de 1996

    for i in range(annos_cotizados):
        anno = datetime.date.today().year - i
        if anno >= 1996 and anno in ipc_ordenado['YEAR'].values:
            ipc_ajuste = 1 + (ipc_ordenado.loc[ipc_ordenado['YEAR'] == anno, 'OBS_VALUE'].values[0] / 100)
        else:
            ipc_ajuste = 1 + (ipc_promedio_pre_1996 / 100)
        
        salario_actual *= ipc_ajuste
        bases_cotizacion.append(salario_actual)

    # Ajustar los meses adicionales cotizados
    if meses_cotizados > 0:
        ipc_ajuste = 1 + (ipc_promedio_pre_1996 / 100)
        base_ajustada = salario_actual * (ipc_ajuste ** (meses_cotizados / 12))  # Ajuste proporcional por meses
        bases_cotizacion.append(base_ajustada)

    return bases_cotizacion

# Función para calcular la base reguladora
def calcular_base_reguladora(bases_ajustadas, anno_jubilacion):
    # Aplicar régimen dual (25 años o 29 años con exclusión de los 2 peores)
    if anno_jubilacion >= 2026:
        bases_relevantes = sorted(bases_ajustadas[-29:])[:-2]  # Tomamos 29 años y excluimos los 2 peores
    else:
        bases_relevantes = bases_ajustadas[-25:] if len(bases_ajustadas) >= 25 else bases_ajustadas
    
    suma_bases = sum(bases_relevantes)
    divisor = 350 if anno_jubilacion < 2026 else len(bases_relevantes) * 14 / 12
    base_reguladora = suma_bases / divisor
    return base_reguladora

# Aplicar el porcentaje según los años y meses cotizados
def aplicar_porcentaje_segun_annos_y_meses(annos_cotizados, meses_cotizados):
    total_meses = annos_cotizados * 12 + meses_cotizados
    if total_meses >= 444:  # 37 años equivalen a 444 meses
        return 1.0  # 100%
    elif total_meses >= 180:  # Mínimo de 15 años equivalen a 180 meses
        meses_adicionales = total_meses - 180
        if meses_adicionales <= 248:
            return 0.5 + (meses_adicionales * 0.21) / 100  # Incremento de 0.21% por mes adicional
        else:
            return 0.5 + (248 * 0.21) / 100 + ((meses_adicionales - 248) * 0.19) / 100
    else:
        return 0.5  # Si tiene al menos 15 años, mínimo el 50%

# Función para calcular la reducción por jubilación anticipada o incremento por demora
def aplicar_ajuste_anticipacion_o_demora(tipo_jubilacion, meses_ajuste, porcentaje_aplicado):
    if tipo_jubilacion == "anticipacion":
        # El coeficiente depende del total de meses de anticipación y años cotizados
        if meses_ajuste <= 24:
            coeficiente = 2.0 / 100  # Para menos de 38.5 años cotizados
        else:
            coeficiente = 1.625 / 100  # Para más de 38.5 años cotizados
        reduccion_total = coeficiente * meses_ajuste
        return max(0, porcentaje_aplicado * (1 - reduccion_total))  # Asegurar que no se reduzca por debajo de 0
    elif tipo_jubilacion == "demora":
        incremento = 0.04 / 12  # Incremento del 4% anual dividido por cada mes adicional
        return porcentaje_aplicado * (1 + incremento * meses_ajuste)
    else:
        return porcentaje_aplicado

# Función para calcular la pensión pública
def calcular_pension_publica(salario_actual, annos_cotizados, meses_cotizados, df_annual_cpi, tipo_jubilacion, meses_ajuste, anno_jubilacion):
    bases_cotizacion = estimar_bases_cotizacion(salario_actual, annos_cotizados, meses_cotizados, df_annual_cpi)
    base_reguladora = calcular_base_reguladora(bases_cotizacion, anno_jubilacion)
    porcentaje_aplicado = aplicar_porcentaje_segun_annos_y_meses(annos_cotizados, meses_cotizados)

    # Aplicar ajuste por anticipación o demora
    porcentaje_aplicado = aplicar_ajuste_anticipacion_o_demora(tipo_jubilacion, meses_ajuste, porcentaje_aplicado)

    # Calcular la pensión mensual
    pension_mensual = (base_reguladora * porcentaje_aplicado) / 12

    # Asegurar que la pensión está dentro de los límites mínimos y máximos de 2024
    pension_minima_anual = 11552.80  # En euros, según normativa de 2024 (sin cónyuge a cargo)
    pension_maxima_anual = 44450.56  # En euros, según normativa de 2024

    # Limitar la pensión mensual dentro de los límites legales
    pension_mensual = max(pension_mensual, pension_minima_anual / 12)  # Garantiza el límite mínimo de pensión
    pension_mensual = min(pension_mensual, pension_maxima_anual / 12)  # Garantiza el límite máximo de pensión

    return pension_mensual

# Ejecución del cálculo
annos_cotizados, meses_cotizados, fecha_nacimiento = estimar_tiempo_cotizado_simplificado()
salario_actual = float(input("Introduce tu salario bruto anual actual: "))
edad_jubilacion_deseada = int(input("Introduce la edad a la que deseas jubilarte: "))
edad_actual = calcular_edad(fecha_nacimiento)
while edad_jubilacion_deseada < edad_actual:
    print("La edad de jubilación deseada debe ser mayor o igual que tu edad actual.")
    edad_jubilacion_deseada = int(input("Introduce la edad a la que deseas jubilarte: "))
    edad_actual = calcular_edad(fecha_nacimiento)
tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, edad_jubilacion_deseada, annos_cotizados)

# Año de jubilación
anno_jubilacion = datetime.date.today().year + (edad_jubilacion_deseada - edad_actual)

# Calcular la pensión mensual
pension_mensual = calcular_pension_publica(salario_actual, annos_cotizados, meses_cotizados, df_annual_cpi, tipo_jubilacion, meses_ajuste, anno_jubilacion)
print(f"Pensión mensual estimada: {pension_mensual:.2f} €")