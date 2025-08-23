
# 🌲 Forest Digital Twin

> A Flask , PostgreSQL , and React  application  for a forest digital twin platform.

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.x-green?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue?logo=postgresql)](https://www.postgresql.org/)

##  Features

-  **User Authentication** (JWT-based signup & login)
-  **Role-Based Access Control** (Admin, Agent, Researcher)
-  **Admin Dashboard** for user and role management
-  **RESTful APIs** for assigning/removing roles
-  **Database Seeding** with default accounts
-  **Secure Password Hashing** with Flask-Bcrypt
-  **CORS Enabled** for frontend integration
-  **Modular Blueprint Structure**

##  Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 16+

### Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone ...
    cd backend
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the database**
    Update the connection string in `config.py`:
    ```python
    SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost:5432/DTDB"
    ```

5.  **Initialize the database**
   ```bash
    # Connect to PostgreSQL and execute the initialization script
    psql -U your_username -d forest_db -f init_database.sql
    ```
    *Replace `your_username` with your PostgreSQL username*
```
6.  **Run the application**
    ```bash

    flask run
    ```
7.  **Open your browser** and navigate to `http://127.0.0.1:5000`


