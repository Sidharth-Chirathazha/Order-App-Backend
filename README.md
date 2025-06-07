Order App Backend
Overview
This is the backend for the Order App, built using Django and Django REST Framework (DRF). The application allows users to submit orders via a frontend form, including product selection and personal information. The backend processes these orders, stores them in a SQLite database, and uses Celery with a Redis broker to asynchronously monitor emails. A Hugging Face model (facebook/bart-large-mnli) is integrated to classify emails and update the order status to "confirmed" when an order confirmation email is detected.
Tech Stack

Django: Web framework for building the backend.
Django REST Framework (DRF): For creating RESTful APIs.
SQLite: Lightweight database for storing order data.
Celery: For asynchronous task processing (e.g., email monitoring).
Redis: Message broker and result backend for Celery.
Hugging Face Model (facebook/bart-large-mnli): For email classification to detect order confirmations.
Python: Programming language (version 3.8+ recommended).

Prerequisites

Python 3.8 or higher
Redis server (for Celery)
Pip (Python package manager)
Virtualenv (optional, but recommended)
A Gmail account for email processing

Setup Instructions

Clone the repository:
git clone https://github.com/Sidharth-Chirathazha/Order-App-Backend.git
cd backend


Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt

Ensure requirements.txt includes:
django
djangorestframework
celery
redis
python-dotenv
transformers


Configure the .env file:Create a .env file in the project root and add the following environment variables:
# .env

# Django secret key (replace with your own secure key in production)
SECRET_KEY=your-django-secret-key

# Debug mode (set to False in production)
DEBUG=True

# Email configuration (use your email service provider's settings)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password

# Frontend URL (used in email confirmation links, etc.)
FRONTEND_URL=http://localhost:5173

# CORS settings (separate multiple URLs with commas)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Celery settings (ensure Redis is running at this address)
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0



SECRET_KEY: Django's secret key for cryptographic signing. Replace with a secure key in production.
DEBUG: Set to False in production for security.
EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD: Configure Gmail SMTP for email processing. Use an App Password for EMAIL_HOST_PASSWORD if 2FA is enabled on the Gmail account.
FRONTEND_URL and CORS_ALLOWED_ORIGINS: Ensure these match the URL of the React frontend.
CELERY_BROKER_URL and CELERY_RESULT_BACKEND: Point to your Redis server.


Apply database migrations:
python manage.py migrate


Start the Redis server:Ensure Redis is running locally or on the specified host. For local setup:
redis-server


Run the Django development server:
python manage.py runserver

The backend will be available at http://localhost:8000.

Start the Celery worker:In a separate terminal, with the virtual environment activated:
celery -A <project_name> worker --loglevel=info

Replace <project_name> with your Django project’s name (e.g., order_app).


API Endpoints

POST /api/orders/: Create a new order.
GET /api/orders/<id>/: Retrieve a specific order by ID.
GET /api/products/: List all Products.
POST /api/confirm-order/<int:id>/: Confirming an Order

Notes

Ensure the Hugging Face model (facebook/bart-large-mnli) is properly configured for email classification. Install the transformers library and verify model availability.
The Celery task monitors emails and updates order status based on the LLM’s classification. Ensure the Gmail account has the necessary permissions and correct credentials.
In production, secure the .env file and use a production-grade database like PostgreSQL instead of SQLite.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

License
This project is licensed under the MIT License.
