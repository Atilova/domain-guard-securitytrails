# Secutirytrails Service
This service is a part of the Domain-Guard system, designed to generate new ***SecurityTrails*** ***accounts*** and extract API keys from the dashboard.

## Features
#### Account Generation
- Automates the creation of new accounts for SecurityTrails using temporary email services (**TenMinuteMail**).

#### CAPTCHA Bypass
- Utilizes an undetectable **SeleniumBase** driver to navigate CAPTCHA challenges.

## Integration
- Employs **RabbitMQ** for message queuing to ensure seamless communication between services.
- Uses **FlaskAPI** during development and debugging.
- Supports random **user-agent** generation.

## Process Orchestrator
- Used to run multiple Selenium driver instances simultaneously using Python's **multiprocessing pool** to increase the account creation rate.
- Uses **Redis** to store current active processes and their actual states.
