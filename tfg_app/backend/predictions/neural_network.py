import torch
import torch.nn as nn
try:
    from tfg_app.backend.pens import estimar_tiempo_cotizado
except ImportError:

import datetime

class PensionPredictor(nn.Module):
    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(in_features=input_size, out_features=hidden_size),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(in_features=hidden_size, out_features=hidden_size//2),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(in_features=hidden_size//2, out_features=output_size),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.network(x)

def preprocess_input(data: dict) -> torch.Tensor | None:
    # Extraer datos del nivel correcto si están anidados
    if 'prev_form' in data and 'prev_form' in data['prev_form']:
        base_data = data['prev_form']['prev_form']
        data2 = data['prev_form']
        data3 = data
    else:
        base_data = data
        data2 = data
        data3 = data

    # Manejar fecha_nacimiento como cadena o datetime.date
    fecha_nacimiento_str = base_data.get('fecha_nacimiento')
    if isinstance(fecha_nacimiento_str, str):
        try:
            fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento_str, "%d/%m/%Y").date()
        except ValueError:
            print(f"Formato inválido para fecha_nacimiento: {fecha_nacimiento_str}")
            return None
    elif isinstance(fecha_nacimiento_str, datetime.date):
        fecha_nacimiento = fecha_nacimiento_str
    else:
        print("fecha_nacimiento no es una cadena ni un objeto date")
        return None

    # Manejar n_hijos como cadena o entero
    n_hijos = base_data.get('n_hijos', 0)
    if isinstance(n_hijos, str):
        if n_hijos.lower() == 'none':
            n_hijos = 0
        else:
            try:
                n_hijos = int(n_hijos)
            except ValueError:
                n_hijos = 0

    try:
        features = [
            float(base_data.get('salario_medio', 0)) / 100000,
            float(base_data.get('edad_jubilacion_deseada', 65)) / 100,
            estimar_tiempo_cotizado(
                fecha_nacimiento,
                base_data.get('edad_inicio_trabajo', 22),
                base_data.get('edad_jubilacion_deseada', 65)
            ) / 50,
            1.0 if str(base_data.get('gender')).lower().startswith('h') else 0.0,
            float(n_hijos) / 5,
            float(base_data.get('n_lagunas', 0)) / 10,
            float(data2.get('aportacion_empresa', 0)) / 10,
            float(data3.get('aportacion_empleado_3p', 0)) / 10000,
            float(data2.get('rentabilidad_2', 0)) / 100,
            float(data3.get('rentabilidad_3', 0)) / 100
        ]
    except Exception as e:
        print(f"Error al generar features: {e}")
        return None
    
    return torch.tensor(features, dtype=torch.float32)

def get_recommendations(scores: torch.Tensor) -> list:
    scores = scores.flatten()
    recommendations = [
        "Deberías aumentar aportaciones al 2º pilar",
        "Deberías invertir más en el 3º pilar",
        "Deberías retrasar la jubilación para maximizar la pensión",
        "Optimizar aportaciones para reducir el IRPF"
    ]
    sorted_recommendations = [(rec, score.item()) for rec, score in zip(recommendations, scores)]
    return sorted(sorted_recommendations, key=lambda x: x[1], reverse=True)