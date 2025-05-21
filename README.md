# Pension Simulator - TFG

**Development and implementation of a pension simulator for the precise estimation of the three pillars of the Spanish system (public, employment, and private), supporting KPMG's digital transformation.**

---

## Description

This project is a pension simulator developed as part of the Final Degree Project (TFG) in Computer Science. The web application allows users to estimate their future pensions by considering the three pillars of the Spanish system: public, employment, and private. Factors such as historical inflation (CPI), contribution gaps, and child-related supplements are taken into account to provide accurate and personalized calculations. The tool is designed to be intuitive, secure, and scalable, meeting usability and accessibility standards (WCAG 2.2).

The simulator is deployed on Reflex Cloud and integrates with services like AWS Cognito for secure user authentication.

---

## Key Features

- **Pension Calculation**: Estimation of the three pillars (public, employment, and private) adjusted for CPI, contribution gaps, and supplements.
- **Secure Authentication**: Integration with AWS Cognito for managing login and data security.
- **Intuitive Interface**: Responsive and accessible design with interactive charts to facilitate result interpretation.
- **External Data Integration**: Use of APIs from the European Central Bank and World Bank for CPI and life expectancy data.
- **Scalability**: Modular architecture that allows for future enhancements and customization.

---

## Technologies Used

- Python - Main programming language.
- Reflex - Framework for creating the web interface.
- Pandas - Data manipulation and analysis.
- ecbdata - Access to European Central Bank data.
- requests - HTTP requests for external APIs.
- AWS Cognito - Authentication and user management.
- GitHub Actions - Continuous integration and automated deployment.
- Reflex Cloud - Deployment platform for Reflex applications.

---

## Installation and Usage

### Prerequisites

- Python 3.12
- Git

### Steps to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/carroyo03/tfg.git
   cd tfg
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the necessary environment variables (e.g., AWS Cognito credentials) in a `.env` file.

4. Run the application:

   ```bash
   reflex run
   ```

5. Open your browser and go to `http://localhost:3000`.

---

## Deployment

The application is deployed on Reflex Cloud, a platform optimized for Reflex-developed applications. Deployment is automated via GitHub Actions, which runs unit tests and deploys the application on every `push` to the main branch, ensuring efficient and secure updates.

---

## Code Structure

The project follows a modular architecture to facilitate maintenance and scalability:

- `backend/`: Contains the business logic, with `main.py` orchestrating integration and `pens.py` implementing the pension simulation formulas.
- `components/`: Reusable UI components (e.g., `accordion.py`, `slider.py`).
- `views/`: Application pages organized by functionality (e.g., `login/`, `pilar1/`, `results/`).
- `tests/`: Unit tests to validate logic and authentication.
- `styles/`: CSS styles for consistent presentation.
- `global_state.py`: Manages the application's global state.
- `tfg_app.py`: Main Reflex configuration.

---

## Testing

The project includes unit tests in `tests/`, covering over 85% of the code (measured with `pytest-cov`). These tests are automatically run on every `push` via the CI pipeline in GitHub Actions, ensuring code integrity.

To run the tests locally:

```bash
pytest
```

---

## Contribution

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a branch for your feature (`git checkout -b feature/new-functionality`).
3. Make your changes and commit (`git commit -m 'Add new functionality'`).
4. Push your branch (`git push origin feature/new-functionality`).
5. Open a Pull Request.

Ensure your changes pass all unit tests.

---

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

---

## Acknowledgments

I thank my TFG director, Victoria López López, and my professors at CUNEF University for their support and teachings. Also, my colleagues at KPMG for their collaboration and my family for their constant motivation.

---

**Author**: Carlos G. Arroyo Lorenzo\
**Date**: May 2025
