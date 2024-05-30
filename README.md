# Domain Guard SecurityTrails Service

This service is a part of the Domain-Guard system, designed to ensure secure and structured domain management by adhering to SOLID, DRY, and Clean Architecture principles.


# Project Structure

- `application/`: Contains application-level logic.
- `domain/`: Defines domain-specific logic and entities.
- `infrastructure/`: Handles external services and infrastructure-related code.
- `integration/`: Manages integration with RabbitMQ and FlaskAPI.
- `utils/`: Utility functions and helpers.


## Features

- **Account Generation**: Automates the creation of new accounts for SecurityTrails using temporary email services (**TenMinuteMail**).
- **CAPTCHA Bypass**: Utilizes an undetectable **seleniumbase** driver to navigate CAPTCHA challenges.
- **Integration**: Employs RabbitMQ for message queuing and Flask API for the integration layer to ensure seamless communication between services.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Atilova/domain-guard-securitytrails.git
   cd domain-guard-securitytrails
   ```

2. **Todo continue**