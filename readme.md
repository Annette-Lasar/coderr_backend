# Backend Project

This is the backend for the Coderr web application. It includes user authentication, a REST API, and database integration.

⚠ **Please clone my version of the frontend instead of using the original one.**

I've made a few minor changes:
- Removed some unintentional trailing HTML tags
- Error warning **"dies ist nur als Kunde möglich"** changed to **"Dies ist nur als Kunde möglich."**
- Added CSS rule for `<p>` elements in the privacy policy (`padding-inline: 1em;`)

*(You're welcome 😉)*  
This ensures that backend integration and layout behave as expected.

---

## Features

- User registration and login
- Token-based authentication
- API endpoints for:
    - login
    - registration
    - profile
    - profiles/business
    - profiles/customer
    - reviews
    - orders
    - offers
    - offerdetails
    - base-info
    - order-count
    - completed-order-count
- Admin interface
- Custom models and serializers

---

## 🛠 Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/Annette-Lasar/coderr_backend.git
    cd coderr_backend
    ```

2. **Create and activate a virtual environment**
    ```bash
    python -m venv env
    ./env/Scripts/activate          # On Windows
    # or
    source env/bin/activate         # macOS / Linux
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**
    ```bash
    python manage.py migrate
    ```

5. **Start the development server**
    ```bash
    python manage.py runserver
    ```

---

## Important: Demo Accounts Setup

To use the **Demo Login buttons** (Guest Customer and Guest Business) in the frontend,  
you need to manually create the following user accounts in your database:

### Customer Demo Account
- Username: `andrey`  
- Password: `asdasd`

### Business Demo Account
- Username: `kevin`  
- Password: `asdasd24`

These users can be created either via the Django admin interface or the registration form —  
whichever method you prefer. Just ensure they have the correct `user_type` set (`customer` or `business`)  
and matching credentials.
