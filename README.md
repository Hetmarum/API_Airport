# API_Airport

A Django REST Framework (DRF) project for managing **airports, routes, flights, airplanes, crews, orders, and tickets**.

---

## Features

- **Custom User model** with email-based authentication  
- **JWT Authentication** with `djangorestframework-simplejwt`  
- **Airport Management** – CRUD for airports, routes, airplanes, airplane types, and crews  
- **Flights & Tickets** – CRUD with filtering, searching, and ordering  
- **Orders & Tickets** – users can create and manage their own orders and tickets  
- **Permissions**:
  - Admin-only access for airports, airplanes, routes, airplane types, and crews
  - Regular users can create/view/update their own orders and tickets
- **Validation**:
  - Prevents duplicate seats for flights  
  - Checks row/seat availability against airplane capacity
- **API Documentation** with **drf-spectacular + Swagger UI**

-**instalation**
 - python -m venv venv
 - source venv/bin/activate       # On Linux/Mac
 - venv\Scripts\activate          # On Windows
 - pip install -r requirements.txt
 - create .env file from .env.sample and populate it with relevant data
 - python manage.py migrate
 - python manage.py createsuperuser
 - python manage.py runserver
