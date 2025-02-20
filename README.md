![logo](static/images/logo.png)

"A rental website where users can rent or list their property easily."

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.1.6-green)
![MySQL](https://img.shields.io/badge/MySQL-9.2-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple)
![Gmail](https://img.shields.io/badge/Gmail-D14836?logo=gmail&logoColor=white)

## Features

- **Backend**: Django 5.1.6
- **Database**: MySQL 9.2 using the **`mysql-connector-python`** driver.
- **Frontend**: Responsive design powered by Bootstrap 5.1.3.
- **Email Integration**: Gmail API for user notifications and communications.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/rahulkumar-fullstack/renthome.git
   cd renthome
   ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**:

   Ensure your MySQL server is running and create a database. Update the `DATABASES` setting in `settings.py` with your database credentials.

5. **Run Migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server**:

   ```bash
   python manage.py runserver
   ```

   Access the application at `http://127.0.0.1:8000/`.

## License

This project is licensed under the **Custom License**.
