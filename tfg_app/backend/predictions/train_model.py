import torch #type:ignore
import torch.nn as nn #type:ignore
import numpy as np #type:ignore
from neural_network import PensionPredictor #type:ignore

def generate_synthetic_data(num_samples:int=1000) -> list:
    
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
        # Heuristic recommendation scores
        scores = [
            0.8 if sample['aportacion_empresa'] < 2 else 0.2,  # Low 2nd pillar
            0.7 if sample['aportacion_empleado_3p'] < 1000 else 0.3,  # Low 3rd pillar
            0.9 if sample['edad_jubilacion_deseada'] < 65 else 0.4,  # Early retirement
            0.6 if sample['salario_medio'] > 50000 else 0.3  # High salary, tax optimization
        ]
        data.append((sample, scores))
    return data


def train_model():
    model = PensionPredictor()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    data = generate_synthetic_data()
    
    for epoch in range(100):
        total_loss = 0
        for sample, target in data:
            inputs = preprocess_input(sample)
            target = torch.tensor(target, dtype=torch.float32)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if epoch % 10 == 0:
            # Print loss every 10 epochs
            print(f"Epoch {epoch+1}, Loss: {total_loss/len(data)}")
    torch.save(model.state_dict(), "pension_model.pth")
    print("Model trained and saved as pension_model.pth")
    
if __name__ == "__main__":
    train_model()
    