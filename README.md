![Renthome log](apps/core/static/core/images/logo.png)

**"A modern, high-performance rental platform for seamless property renting and listing."**

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.1.6-green)
![MySQL](https://img.shields.io/badge/MySQL-9.2-blue)
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.34.0-yellow)
![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-4.0-cyan)
![Gmail](https://img.shields.io/badge/Gmail-D14836?logo=gmail&logoColor=white)

---

## 🚀 About the Project

RentHome is a **fully asynchronous** rental platform built with **Django ASGI and Uvicorn**, ensuring **high performance** and **scalability**. The UI is designed with **Tailwind CSS** for a **lightweight and modern** experience.

### ✨ Features

- **Fast & Scalable**: Built with **Django ASGI + Uvicorn** for non-blocking performance.
- **Tenant Dashboard**: View upcoming rent, rent duration, and book multiple properties.
- **Landlord Dashboard**: List properties with images, SEO-optimized keywords, pricing, and facilities.
- **Email Notifications**: Powered by **Gmail SMTP** for important updates.
- **Modern UI**: Styled using **Tailwind CSS** with **Node.js package management**.

---

## ⚡ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/rahulkumar-fullstack/renthome.git
cd renthome
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# Windows: venv\Scripts\activate
```

### 3️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure MySQL Database

- Ensure **MySQL is running**.
- Create a database and update `DATABASES` in `settings.py` with your credentials.

### 5️⃣ Apply Migrations

```bash
python manage.py migrate
```

### 6️⃣ Install Node.js Dependencies (For Tailwind CSS only)

Ensure **Node.js & npm** are installed, then run:

```bash
npm install
```

_(No need to recompile Tailwind unless changes are made. If required, use the command below.)_

```bash
npx @tailwindcss/cli -i apps/core/static/core/css/tailwind_custom.css -o apps/core/static/core/css/custom.css --watch
```

### 7️⃣ Collect Static Files

```bash
python manage.py collectstatic
```

### 8️⃣ Start the Development Server

```bash
uvicorn renthome.asgi:application --host 127.0.0.1 --port 8000 --reload
```

🔗 Access the app: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 📜 License

This project is licensed under the **Custom License**.
