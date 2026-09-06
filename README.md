# Gudibanda Kalyana Mandapam Availability Portal

A web-based availability information portal for checking the availability status of Gudibanda Kalyana Mandapam dates.

The application provides a calendar-based interface where users can view available, booked, pending, and blocked dates. When a user wants to make an actual booking, they are redirected to the official Tirumala Tirupati Devasthanams (TTD) website.

## 🚀 Features

* User Registration and Login
* Secure Password Hashing
* Availability Calendar
* Available Date Status
* Booked Date Status
* Pending Date Status
* Blocked Date Status
* Admin Dashboard
* Admin can block dates
* Admin can unblock dates
* Registered user management
* Responsive web interface
* Redirect to official TTD website for actual booking

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Database

* MySQL

### Security

* Werkzeug Password Hashing
* Flask Sessions

## 📅 Availability Status

The calendar displays dates using different statuses:

| Status       | Meaning                        |
| ------------ | ------------------------------ |
| 🟢 Available | Date is available              |
| 🔴 Booked    | Date has already been booked   |
| 🟡 Pending   | Booking is pending             |
| 🌸 Blocked   | Date has been blocked by admin |
| ⚪ Past       | Date has already passed        |

## 🏗️ Project Structure

```text
Gudibanda-Kalyana-Mandapam/
│
├── app.py
├── README.md
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── availability.html
│   ├── dashboard.html
│   ├── book.html
│   └── admin.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── availability.css
│   │   └── admin.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── images/
│       └── kalyanam.webp
│
└── requirements.txt
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project

```bash
cd Gudibanda-Kalyana-Mandapam
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

Create a MySQL database:

```sql
CREATE DATABASE gudibanda_kalyana;
```

Create the required tables:

* `users`
* `bookings`
* `blocked_dates`

Update the MySQL connection details in `app.py` according to your local environment.

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## 👨‍💼 Admin Access

The administrator can:

* Access the Admin Dashboard
* Block unavailable dates
* Unblock dates
* View registered users
* Manage availability information

The admin role is stored in the `users` table.

## 🛕 Official TTD Booking

This application is an **independent availability information portal**.

Actual booking, payment, and confirmation are handled through the official TTD website:

https://tirupatibalaji.ap.gov.in/#/kmCal

When users select an available date, the application provides access to the official TTD booking website.

## 🔐 Security

The application uses:

* Password hashing using Werkzeug
* Flask session-based authentication
* Admin role verification
* Form validation
* Database-backed user authentication

## 🎯 Project Objective

The main objective of this project is to provide a simple and user-friendly calendar interface for viewing mandapam availability while directing users to the official TTD website for actual booking.

## 🔮 Future Improvements

* Online notifications
* Email notifications
* Better admin analytics
* Monthly availability reports
* Cloud deployment
* Production database
* Improved mobile UI
* Automated availability synchronization where officially permitted

## 👨‍💻 Author

**Naveen**

B.Tech Computer Science Graduate

## 📌 Disclaimer

This project is an independent availability information portal and is not an official website or service of Tirumala Tirupati Devasthanams (TTD).

Users should use the official TTD website for actual booking, payment, and confirmation.
