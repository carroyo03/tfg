import datetime
from dateutil import parser # type: ignore
from ecbdata import ecbdata as ecb # type: ignore
import pandas as pd

# Valores constantes
COMPLEMENTO_MENSUAL_POR_HIJO = 33.20 # En euros, según normativa de 2024
MAX_HIJOS_APLICABLES = 4
IPC_PROMEDIO_PRE_1996 = 2.5  # Asumimos un 2.5% de inflación anual antes de 1996

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
    fecha_nacimiento = parser.parse(input("Introduce tu fecha de nacimiento (formato: dd/mm/aaaa): ")).date()
    edad_inicio_trabajo = validar_entrada_numerica("¿A qué edad comenzaste a trabajar aproximadamente? (Ej: 22): ", valor_minimo=16)
    
    mes_inicio_trabajo = 6  # Predeterminado como Junio
    dia_inicio_trabajo = 15  # Día predeterminado
    fecha_inicio_trabajo = datetime.date(fecha_nacimiento.year + int(edad_inicio_trabajo), mes_inicio_trabajo, dia_inicio_trabajo)

    fecha_actual = datetime.date.today()
    delta = fecha_actual - fecha_inicio_trabajo
    annos_cotizados = delta.days // 365
    meses_cotizados = (delta.days % 365) // 30
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
    ipc_promedio_pre_1996 = IPC_PROMEDIO_PRE_1996  # Asumimos un 2.5% de inflación anual antes de 1996

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
    
# Función para validar entrada numérica
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

# Preguntar por género y número de hijos
def solicitar_datos_genero_y_hijos():
    genero = input("Introduce tu género (hombre/mujer): ").strip().lower()
    while genero not in ["hombre", "mujer"]:
        print("Por favor, introduce 'hombre' o 'mujer'.")
        genero = input("Introduce tu género (hombre/mujer): ").strip().lower()

    numero_hijos = validar_entrada_numerica("Introduce el número de hijos que tienes: ", valor_minimo=0)
    return genero, int(numero_hijos)

# Función para calcular el complemento por brecha de género en función del número de hijos
def calcular_complemento_por_hijos(genero, numero_hijos, tipo_jubilacion):
    
    complemento_por_hijo = COMPLEMENTO_MENSUAL_POR_HIJO
    # Máximo de 4 hijos aplicables
    if genero == "mujer" and tipo_jubilacion != "anticipacion":
        # Las mujeres tienen derecho al complemento directamente
        return min(complemento_por_hijo * numero_hijos, complemento_por_hijo * MAX_HIJOS_APLICABLES)
    
        # Si no tiene hijos, no se aplica el complemento
    elif genero == "hombre" and tipo_jubilacion != "anticipacion" and numero_hijos >= 2:
        # Los hombres pueden recibir el complemento solo si cumplen condiciones específicas
        # Ejemplo: si interrumpieron su carrera laboral o son viudos
        interrupcion_carrera = input("¿Has interrumpido tu carrera profesional debido al nacimiento o cuidado de tus hijos? (si/no): ").strip().lower()
        if interrupcion_carrera == "si":
            return min(complemento_por_hijo * numero_hijos, complemento_por_hijo * MAX_HIJOS_APLICABLES)
    return 0.0


# Función para calcular la pensión pública, incluyendo el complemento por hijos si aplica
def calcular_pension_publica(salario_actual, annos_cotizados, meses_cotizados, df_annual_cpi, tipo_jubilacion, meses_ajuste, anno_jubilacion, genero, numero_hijos):
    # Validación de años mínimos cotizados
    if annos_cotizados < 15:
        print("No tienes derecho a una pensión contributiva, ya que no has cotizado los 15 años mínimos requeridos.")
        return 0.0

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

    # Calcular el complemento por hijos si aplica
    complemento = calcular_complemento_por_hijos(genero, numero_hijos, tipo_jubilacion)
    pension_mensual += complemento  # Añadir el complemento por hijos como cantidad fija

    return pension_mensual

# Recogida de información del segundo pilar del usuario
def solicitar_datos_segundo_pilar():
    print("\nAhora vamos a calcular tu plan de pensión del segundo pilar (proporcionado por la empresa).")
    print("Si no tienes un plan de pensiones con tu empresa, puedes omitir esta sección.")

    tiene_segundo_pilar = input("¿Tienes un plan de pensión proporcionado por tu empresa? (si/no): ").strip().lower()
    if tiene_segundo_pilar == "no":
        return None  # El usuario no tiene un plan del segundo pilar

    contribucion_personal = float(input("¿Cuánto porcentaje de tu salario anual aportas al plan de pensiones? (en %): "))
    contribucion_empresa = float(input("¿Cuánto porcentaje de tu salario anual aporta tu empresa? (en %): "))

    return {
        "contribucion_personal": contribucion_personal,
        "contribucion_empresa": contribucion_empresa
    }

# Calcular el ahorro acumulado del segundo pilar
def calcular_acumulado_segundo_pilar(salario_actual, annos_cotizados, datos_segundo_pilar):
    if datos_segundo_pilar is None:
        return 0  # No hay contribuciones al segundo pilar si el usuario no tiene plan

    contribucion_anual_personal = salario_actual * (datos_segundo_pilar["contribucion_personal"] / 100)
    contribucion_anual_empresa = salario_actual * (datos_segundo_pilar["contribucion_empresa"] / 100)
    contribucion_total_anual = contribucion_anual_personal + contribucion_anual_empresa

    # Ahorro acumulado sin rendimiento
    ahorro_acumulado = contribucion_total_anual * annos_cotizados

    return ahorro_acumulado

# Proyectar el pago mensual estimado en la jubilación a partir del segundo pilar
def calcular_pension_segundo_pilar(ahorro_acumulado_segundo_pilar, annos_jubilacion=20):
    if ahorro_acumulado_segundo_pilar == 0:
        return 0

    # Dividimos el total acumulado entre el número de meses durante el retiro
    meses_jubilacion = annos_jubilacion * 12
    pension_mensual_segundo_pilar = ahorro_acumulado_segundo_pilar / meses_jubilacion

    return pension_mensual_segundo_pilar


# Función para solicitar datos sobre el tercer pilar
def solicitar_datos_tercer_pilar():
    print("\nAhora vamos a calcular tu plan de pensión del tercer pilar (plan de pensiones privado).")
    print("Si no tienes un plan de pensiones privado, puedes omitir esta sección.")

    tiene_tercer_pilar = input("¿Tienes un plan de pensión privado? (si/no): ").strip().lower()
    if tiene_tercer_pilar == "no":
        return None  # El usuario no tiene un plan del tercer pilar

    contribucion_anual = float(input("¿Cuánto aportas anualmente a tu plan de pensiones privado (en euros)?: "))
    rendimiento_anual = float(input("Introduce el rendimiento anual estimado de tu plan de pensiones privado (en %): "))

    return {
        "contribucion_anual": contribucion_anual,
        "rendimiento_anual": rendimiento_anual
    }

# Función para calcular el ahorro acumulado del tercer pilar
def calcular_acumulado_tercer_pilar(annos_cotizados, datos_tercer_pilar):
    if datos_tercer_pilar is None:
        return 0  # No hay contribuciones al tercer pilar si el usuario no tiene plan

    contribucion_anual = datos_tercer_pilar["contribucion_anual"]
    rendimiento_anual = datos_tercer_pilar["rendimiento_anual"] / 100

    # Limitar el rendimiento anual a un valor razonable
    rendimiento_anual = min(rendimiento_anual, 0.05)  # Máximo 5% de rendimiento anual

    # Ahorro acumulado con interés compuesto
    if rendimiento_anual > 0:
        ahorro_acumulado = contribucion_anual * (((1 + rendimiento_anual) ** annos_cotizados - 1) / rendimiento_anual)
    else:
        ahorro_acumulado = contribucion_anual * annos_cotizados

    return ahorro_acumulado

# Función para calcular la pensión del tercer pilar
def calcular_pension_tercer_pilar(ahorro_acumulado_tercer_pilar, annos_jubilacion=20):
    if ahorro_acumulado_tercer_pilar == 0:
        return 0

    # Dividimos el total acumulado entre el número de meses durante el retiro
    meses_jubilacion = annos_jubilacion * 12
    pension_mensual_tercer_pilar = ahorro_acumulado_tercer_pilar / meses_jubilacion

    return pension_mensual_tercer_pilar

def calcular_pensiones(fecha_nacimiento_str, edad_inicio_trabajo, salario, edad_jubilacion_deseada, genero, numero_hijos, porcentaje_personal, porcentaje_empresa, contribucion_privada, rendimiento_privado):
    """
    Esta función principal orquesta todo el cálculo de las pensiones.
    """

    # Convertir fecha de nacimiento
    fecha_nacimiento = parser.parse(fecha_nacimiento_str).date()

    # Cálculo del primer pilar
    edad_actual = calcular_edad(fecha_nacimiento)
    annos_cotizados, meses_cotizados, _ = estimar_tiempo_cotizado_simplificado(fecha_nacimiento, edad_inicio_trabajo)
    tipo_jubilacion, meses_ajuste = calcular_annos_anticipacion_o_demora(edad_actual, edad_jubilacion_deseada, annos_cotizados)
    anno_jubilacion = datetime.date.today().year + (edad_jubilacion_deseada - edad_actual)
    pension_primer_pilar = calcular_pension_publica(salario, annos_cotizados, meses_cotizados, df_annual_cpi, tipo_jubilacion, meses_ajuste, anno_jubilacion, genero, numero_hijos)

    # Cálculo del segundo pilar
    ahorro_segundo_pilar = calcular_acumulado_segundo_pilar(salario, annos_cotizados, {"contribucion_personal": porcentaje_personal, "contribucion_empresa": porcentaje_empresa})
    pension_segundo_pilar = calcular_pension_segundo_pilar(ahorro_segundo_pilar)

    # Cálculo del tercer pilar
    ahorro_tercer_pilar = calcular_acumulado_tercer_pilar(annos_cotizados, {"contribucion_anual": contribucion_privada, "rendimiento_anual": rendimiento_privado})
    pension_tercer_pilar = calcular_pension_tercer_pilar(ahorro_tercer_pilar)

    # Calcular pensión total
    pension_total = pension_primer_pilar + pension_segundo_pilar + pension_tercer_pilar
    return pension_total
