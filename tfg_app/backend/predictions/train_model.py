import torch
import torch.nn as nn
import numpy as np
try:
    from tfg_app.backend.predictions.neural_network import PensionPredictor, preprocess_input
except ImportError:
    from neural_network import PensionPredictor, preprocess_input
from torch.nn import MSELoss

def generate_synthetic_data(num_samples: int = 1000) -> list:
    data = []
    for _ in range(num_samples):
        sample = {
            'salario_medio': np.random.uniform(20000, 100000),
            'edad_jubilacion_deseada': np.random.randint(60, 70),
            'fecha_nacimiento': '01/01/' + str(2025 - np.random.randint(35, 65)),
            'edad_inicio_trabajo': np.random.randint(18, 30),
            'gender': 'Hombre' if np.random.rand() > 0.5 else 'Mujer',
            'n_hijos': np.random.randint(0, 5),
            'n_lagunas': np.random.uniform(0, 5),
            'aportacion_empresa': np.random.uniform(0, 5),
            'aportacion_empleado_3p': np.random.uniform(0, 5000),
            'rentabilidad_2': np.random.uniform(1, 5),
            'rentabilidad_3': np.random.uniform(1, 5)
        }
        if all([type(sample.get(key)) in [int, float] for key in ['salario_medio', 'edad_jubilacion_deseada', 'aportacion_empresa', 'aportacion_empleado_3p']]):
            scores = [
                np.random.uniform(7, 10) / 10 if sample['aportacion_empresa'] < 2 else np.random.uniform(0, 2) / 10,
                np.random.uniform(6, 10) / 10 if sample['aportacion_empleado_3p'] < 1000 else np.random.uniform(0, 4) / 10,
                np.random.uniform(8, 10) / 10 if sample['edad_jubilacion_deseada'] < 65 else np.random.uniform(3, 7) / 10,
                np.random.uniform(6, 10) / 10 if sample['salario_medio'] > 50000 else np.random.uniform(0, 5) / 10
            ]
            data.append((sample, scores))
    print(f"Generated {len(data)} valid samples for training")
    # Imprimir algunos datos y scores para verificar
    if data:
        print(f"Sample data: {data[0][0]}")
        print(f"Sample scores: {data[0][1]}")
    return data

def train_model():
    model = PensionPredictor(input_size=10, hidden_size=64, output_size=4)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    data = generate_synthetic_data()
    if not data:
        print("No valid data to train on!")
        return
    
    num_valid_samples = 0
    for epoch in range(100):
        total_loss = 0
        for i, (sample, target) in enumerate(data):
            inputs = preprocess_input(sample)
            if inputs is None:
                print(f"Sample {i} skipped: preprocess_input returned None")
                continue
            num_valid_samples += 1
            # Asegurarse de que inputs tenga forma (1, 10)
            if len(inputs.shape) == 1:
                inputs = inputs.unsqueeze(0)  # Añadir dimensión batch
            target = torch.tensor(target, dtype=torch.float32).unsqueeze(0)  # Añadir dimensión batch
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, target)
            
            # Depuración
            if i % 100 == 0:  # Imprimir cada 100 muestras
                print(f"Epoch {epoch + 1}, Sample {i}:")
                print(f"  Inputs: {inputs}")
                print(f"  Outputs: {outputs}")
                print(f"  Target: {target}")
                print(f"  Loss: {loss.item()}")
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            avg_loss = total_loss / max(num_valid_samples, 1)  # Evitar división por 0
            print(f"Epoch {epoch + 1}, Loss: {avg_loss}, Valid samples processed: {num_valid_samples}")
    
    torch.save(model.state_dict(), "pension_model.pth")
    print("Model trained and saved as pension_model.pth")

if __name__ == "__main__":
    train_model()