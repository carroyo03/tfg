import torch #type:ignore
import torch.nn as nn #type:ignore
from tfg_app.backend.pens import estimar_tiempo_cotizado #type:ignore
import datetime #type:ignore

class PensionPredictor(nn.Module):
    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(in_features= input_size, out_features = hidden_size), #input_size = 3, hidden_size = 5
            nn.ReLU(),
            nn.Dropout(p = 0.2),
            nn.Linear(in_features = hidden_size, out_features = hidden_size//2),
            nn.ReLU(),
            nn.Dropout(p = 0.2),
            nn.Linear(in_features = hidden_size//2, out_features = output_size), #output_size = 1
            nn.Sigmoid() # Output scores between 0 and 1
        )
        
    def forward(self, x):
        return self.network(x)


def preprocess_input(data : dict) -> torch.Tensor | None:
    
    fecha_nacimiento = data.get('fecha_nacimiento') if type(data.get('fecha_nacimiento')) == datetime.date else None
    
    if fecha_nacimiento is None:
        return None
    features = [
        float(data.get('salario_medio', 0)) / 100000,
        float(data.get('edad_jubilacion_deseada', 65)) / 100,
        estimar_tiempo_cotizado(fecha_nacimiento,
                                data.get('edad_inicio_trabajo',22),
                                data.get('edad_jubilacion_deseada', 65)
        ) / 50,
        1.0 if str(data.get('gender')).lower().startswith('h') else 0.0,
        float(data.get('n_hijos', 0)) / 5,
        float(data.get('n_lagunas', 0)) / 10,  # Normalize lagunas
        float(data.get('aportacion_empresa', 0)) / 10,  # Normalize 2nd pillar
        float(data.get('aportacion_empleado_3p', 0)) / 10000,  # Normalize 3rd pillar
        float(data.get('rentabilidad_2', 0)) / 100,  # Normalize return
        float(data.get('rentabilidad_3', 0)) / 100  # Normalize return
    ]
    
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


        