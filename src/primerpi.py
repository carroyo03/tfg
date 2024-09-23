import pandas as pd

tipo_jubilacion = input("Introduce el tipo de jubilación (ordinaria, anticipada o prolongada): ")
while tipo_jubilacion.lower() not in ["ordinaria", "anticipada", "prolongada"]:
    print('Tipo de jubilación no válido')
    tipo_jubilacion = input("Introduce un tipo de jubilación válido (ordinaria, anticipada o prolongada): ")

match tipo_jubilacion:
    case "anticipada":
        print("Jubilación anticipada")
    case "prolongada":
        print("Jubilación prolongada")

print('-'*50)

print("Mi jubilación:")

print('-'*50)


