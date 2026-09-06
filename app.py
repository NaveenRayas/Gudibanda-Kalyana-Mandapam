import os
import tempfile
from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)

app.secret_key = "gudibanda-secret-key"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_ssl_ca_path():
    """
    Resolves the SSL CA certificate path for Aiven MySQL.
    Supports:
    1. Direct certificate content via AIVEN_CA_CERT (or AIVEN_SSL_CA containing PEM text).
    2. Path configured via AIVEN_SSL_CA environment variable.
    3. Render secret file path (/etc/secrets/ca.pem).
    4. ca.pem located in the project root directory.
    5. Local Windows development fallback (C:/Users/TECQNIO/Downloads/ca.pem).
    """
    cert_content = os.getenv("AIVEN_CA_CERT")
    ssl_ca_env = os.getenv("AIVEN_SSL_CA")

    # If AIVEN_SSL_CA contains the raw certificate text instead of a file path
    if ssl_ca_env and "-----BEGIN CERTIFICATE-----" in ssl_ca_env:
        cert_content = ssl_ca_env
        ssl_ca_env = None

    # If raw certificate text was provided, write to a temporary file
    if cert_content:
        ca_path = os.path.join(tempfile.gettempdir(), "aiven_ca.pem")
        with open(ca_path, "w", encoding="utf-8") as f:
            f.write(cert_content.strip())
        return ca_path

    # Check path provided via AIVEN_SSL_CA environment variable
    if ssl_ca_env and os.path.exists(ssl_ca_env):
        return ssl_ca_env

    # Check Render Secret File location
    render_secret_path = "/etc/secrets/ca.pem"
    if os.path.exists(render_secret_path):
        return render_secret_path

    # Check project folder
    project_ca_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ca.pem")
    if os.path.exists(project_ca_path):
        return project_ca_path

    # Local fallback for existing Windows development setup
    local_fallback = "C:/Users/TECQNIO/Downloads/ca.pem"
    if os.path.exists(local_fallback):
        return local_fallback

    return ssl_ca_env or local_fallback


def get_db_connection():
    connection = mysql.connector.connect(
        host="gudibanda-mysql-gudibanda.f.aivencloud.com",
        port=26828,
        user="avnadmin",
        password=os.getenv("AIVEN_DB_PASSWORD"),
        database="gudibanda_kalyana",
        ssl_ca=get_ssl_ca_path()
    )

    return connection

# ==========================================
# HOME
# ==========================================

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    # ==========================================
    # CHECK DATABASE STATUS
    # ==========================================

    try:
        connection = get_db_connection()
        connection.close()
        db_status = True

    except Exception:
        db_status = False

    return render_template(
        "index.html",
        db_status=db_status
    )

# ==========================================
# AVAILABILITY PAGE
# ==========================================

@app.route("/availability")
def availability():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("availability.html")

# ==========================================
# About / Contact PAGE
# ==========================================

@app.route("/about")
def about():
    return render_template("about.html")

# ==========================================
# AVAILABILITY API
# ==========================================

@app.route("/api/availability")
def api_availability():

    year = request.args.get("year")
    month = request.args.get("month")

    if not year or not month:

        return {
            "booked": [],
            "pending": [],
            "blocked": []
        }


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # JavaScript:
        # January = 0
        #
        # MySQL:
        # January = 1

        mysql_month = int(month) + 1


        # ==========================================
        # GET BOOKINGS
        # ==========================================

        query = """
            SELECT booking_date, status
            FROM bookings
            WHERE YEAR(booking_date) = %s
            AND MONTH(booking_date) = %s
        """

        cursor.execute(
            query,
            (year, mysql_month)
        )

        bookings = cursor.fetchall()


        # ==========================================
        # GET BLOCKED DATES
        # ==========================================

        query = """
            SELECT blocked_date
            FROM blocked_dates
            WHERE YEAR(blocked_date) = %s
            AND MONTH(blocked_date) = %s
        """

        cursor.execute(
            query,
            (year, mysql_month)
        )

        blocked_dates = cursor.fetchall()


        booked = []
        pending = []
        blocked = []


        # ==========================================
        # PROCESS BOOKINGS
        # ==========================================

        for booking in bookings:

            booking_date = booking["booking_date"]

            formatted_date = booking_date.strftime(
                "%Y-%m-%d"
            )


            if booking["status"] == "approved":

                booked.append(formatted_date)


            elif booking["status"] == "pending":

                pending.append(formatted_date)


        # ==========================================
        # PROCESS BLOCKED DATES
        # ==========================================

        for item in blocked_dates:

            blocked.append(
                item["blocked_date"].strftime(
                    "%Y-%m-%d"
                )
            )


        return {
            "booked": booked,
            "pending": pending,
            "blocked": blocked
        }


    finally:

        cursor.close()
        connection.close()


# ==========================================
# REGISTER
# ==========================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]


        # ==========================================
        # HASH PASSWORD
        # ==========================================

        hashed_password = generate_password_hash(
            password
        )


        connection = get_db_connection()

        cursor = connection.cursor()


        try:

            query = """
                INSERT INTO users
                (
                    name,
                    email,
                    password
                )
                VALUES (%s, %s, %s)
            """

            values = (
                name,
                email,
                hashed_password
            )


            cursor.execute(
                query,
                values
            )


            connection.commit()


            return redirect ("/")


        except mysql.connector.IntegrityError:

                            return """
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Email Already Registered</title>

                                <style>
                                    body {
                                        margin: 0;
                                        font-family: Arial, sans-serif;
                                        background: #fffdf9;
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        height: 100vh;
                                    }

                                    .message-box {
                                        background: white;
                                        padding: 35px;
                                        width: 350px;
                                        text-align: center;
                                        border-radius: 15px;
                                        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
                                    }

                                    .message-box h2 {
                                        color: #d9534f;
                                        margin-bottom: 10px;
                                    }

                                    .message-box p {
                                        color: #666;
                                        margin-bottom: 25px;
                                    }

                                    .login-btn {
                                        display: inline-block;
                                        padding: 11px 25px;
                                        background: #b88935;
                                        color: white;
                                        text-decoration: none;
                                        border-radius: 25px;
                                        font-weight: bold;
                                    }

                                    .login-btn:hover {
                                        background: #a57425;
                                    }
                                </style>
                            </head>

                            <body>

                                <div class="message-box">

                                    <h2>⚠️ Email Already Registered!</h2>

                                    <p>
                                        This email is already registered.
                                        Please login to continue.
                                    </p>

                                    <a href="/login" class="login-btn">
                                        Go to Login
                                    </a>

                                </div>

                            </body>
                            </html>
                            """

            


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "register.html"
    )


# ==========================================
# LOGIN
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        try:

            query = """
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role
                FROM users
                WHERE email = %s
            """


            cursor.execute(
                query,
                (email,)
            )


            user = cursor.fetchone()


            # ==========================================
            # CHECK LOGIN
            # ==========================================

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]

                session["user_name"] = user["name"]

                session["user_role"] = user["role"]


                # ==========================================
                # ADMIN
                # ==========================================

                if user["role"] == "admin":

                    return redirect("/admin")


                # ==========================================
                # NORMAL USER
                # ==========================================

                return redirect("/")


            # ==========================================
            # INVALID LOGIN
            # ==========================================

            return """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Login Failed | Gudibanda</title>


    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }


        body {

            font-family: Arial, sans-serif;

            min-height: 100vh;

            display: flex;

            justify-content: center;

            align-items: center;

            background: #f8f5f0;
        }


        .error-container {

            width: 90%;

            max-width: 450px;

            background: white;

            padding: 45px 35px;

            border-radius: 15px;

            text-align: center;

            box-shadow:
                0 10px 30px rgba(0, 0, 0, 0.12);
        }


        .error-icon {

            width: 70px;

            height: 70px;

            margin: 0 auto 20px;

            display: flex;

            justify-content: center;

            align-items: center;

            border-radius: 50%;

            background: #ffe5e5;

            color: #d32f2f;

            font-size: 35px;
        }


        h2 {

            color: #333;

            margin-bottom: 12px;
        }


        p {

            color: #666;

            margin-bottom: 30px;

            line-height: 1.6;
        }


        .login-button {

            display: inline-block;

            padding: 13px 28px;

            background: #8b5e34;

            color: white;

            text-decoration: none;

            border-radius: 8px;

            font-size: 16px;

            font-weight: bold;

            transition: 0.3s;
        }


        .login-button:hover {

            background: #6f4728;

            transform: translateY(-2px);
        }

    </style>

</head>


<body>


    <div class="error-container">


        <div class="error-icon">

            ✕

        </div>


        <h2>

            Login Failed ❌

        </h2>


        <p>

            Invalid email or password.

            <br>

            Please check your details and try again.

        </p>


        <a
            href="/login"
            class="login-button">

            ← Go Back to Login

        </a>


    </div>


</body>

</html>
"""


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "login.html"
    )


# ==========================================
# USER DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")


    return render_template(
        "dashboard.html"
    )


# ==========================================
# BOOKING
# ==========================================

@app.route(
    "/book",
    methods=["GET", "POST"]
)
def book():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_id" not in session:

        return redirect("/login")


    # ==========================================
    # GET REQUEST
    # ==========================================

    if request.method == "GET":

        booking_date = request.args.get("date")


        if not booking_date:

            return redirect("/availability")


        # ==========================================
        # CHECK DATE FORMAT
        # ==========================================

        try:

            selected_date = date.fromisoformat(
                booking_date
            )

        except ValueError:

            return redirect("/availability")


        # ==========================================
        # PREVENT PAST DATE
        # ==========================================

        today = date.today()


        if selected_date < today:

            return """
                <!DOCTYPE html>

                <html>

                <head>

                    <title>Invalid Date</title>

                    <style>

                        body {

                            font-family: Arial;

                            background: #f8f5f0;

                            min-height: 100vh;

                            display: flex;

                            justify-content: center;

                            align-items: center;
                        }


                        .box {

                            background: white;

                            padding: 40px;

                            border-radius: 15px;

                            text-align: center;

                            box-shadow:
                                0 10px 30px
                                rgba(0,0,0,0.12);
                        }


                        h2 {

                            color: #d32f2f;

                            margin-bottom: 15px;
                        }


                        p {

                            color: #666;

                            margin-bottom: 20px;
                        }


                        a {

                            display: inline-block;

                            padding: 12px 22px;

                            background: #8b5e34;

                            color: white;

                            text-decoration: none;

                            border-radius: 8px;
                        }

                    </style>

                </head>


                <body>

                    <div class="box">

                        <h2>
                            Sorry! You cannot book a past date ❌
                        </h2>

                        <p>
                            Please select a future date.
                        </p>

                        <a href="/availability">
                            Back to Availability
                        </a>

                    </div>

                </body>

                </html>
            """


        return render_template(
            "book.html",
            booking_date=booking_date
        )


    # ==========================================
    # POST REQUEST
    # ==========================================

    booking_date = request.form["booking_date"]

    event_type = request.form["event_type"]

    notes = request.form.get(
        "notes",
        ""
    )


    # ==========================================
    # CHECK DATE FORMAT
    # ==========================================

    try:

        selected_date = date.fromisoformat(
            booking_date
        )

    except ValueError:

        return """
            <h2>
                Invalid booking date ❌
            </h2>

            <a href="/availability">
                Back to Availability
            </a>
        """


    # ==========================================
    # PREVENT PAST DATE
    # ==========================================

    today = date.today()


    if selected_date < today:

        return """
            <h2>
                Sorry! You cannot book a past date ❌
            </h2>

            <p>
                Please select a future date.
            </p>

            <a href="/availability">
                Back to Availability
            </a>
        """


    user_id = session["user_id"]


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        # ==========================================
        # CHECK BLOCKED DATE
        # ==========================================

        query = """
            SELECT id
            FROM blocked_dates
            WHERE blocked_date = %s
        """


        cursor.execute(
            query,
            (booking_date,)
        )


        blocked = cursor.fetchone()


        if blocked:

            return """
                <h2>
                    Sorry! This date is blocked ❌
                </h2>

                <a href="/availability">
                    Back to Availability
                </a>
            """


        # ==========================================
        # CHECK EXISTING BOOKING
        # ==========================================

        query = """
            SELECT
                id,
                status
            FROM bookings
            WHERE booking_date = %s
            AND status IN ('approved', 'pending')
        """


        cursor.execute(
            query,
            (booking_date,)
        )


        existing_booking = cursor.fetchone()


        if existing_booking:

            if existing_booking["status"] == "approved":

                return """
                    <h2>
                        Sorry! This date is already booked ❌
                    </h2>

                    <a href="/availability">
                        Back to Availability
                    </a>
                """


            if existing_booking["status"] == "pending":

                return """
                    <h2>
                        This date already has
                        a pending booking request ⏳
                    </h2>

                    <a href="/availability">
                        Back to Availability
                    </a>
                """


        # ==========================================
        # INSERT BOOKING
        # ==========================================

        query = """
            INSERT INTO bookings
            (
                user_id,
                booking_date,
                event_type,
                status,
                notes
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'pending',
                %s
            )
        """


        values = (
            user_id,
            booking_date,
            event_type,
            notes
        )


        cursor.execute(
            query,
            values
        )


        connection.commit()


        # ==========================================
        # SUCCESS
        # ==========================================

        return f"""
            <h2>
                Booking Request Submitted Successfully! ✅
            </h2>

            <p>
                Your booking request is now pending approval.
            </p>

            <p>
                Booking Date:
                <strong>{booking_date}</strong>
            </p>

            <p>
                Event Type:
                <strong>{event_type}</strong>
            </p>

            <br>

            <a href="/dashboard">
                Go to Dashboard
            </a>
        """


    finally:

        cursor.close()
        connection.close()


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():

    # CHECK LOGIN
    if "user_id" not in session:
        return redirect("/login")


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # ==========================================
        # GET CURRENT USER FROM DATABASE
        # ==========================================

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()


        # ==========================================
        # USER NOT FOUND
        # ==========================================

        if not user:

            session.clear()

            return redirect("/login")


        # ==========================================
        # CHECK ADMIN
        # ==========================================

        if user["role"] != "admin":

            return """
                <!DOCTYPE html>

                <html>

                <head>

                    <title>Access Denied</title>

                    <style>

                        body {
                            font-family: Arial, sans-serif;
                            background: #f8f5f0;
                            min-height: 100vh;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }

                        .box {
                            background: white;
                            padding: 40px;
                            border-radius: 15px;
                            text-align: center;
                            box-shadow:
                                0 10px 30px
                                rgba(0,0,0,0.12);
                        }

                        h2 {
                            color: #d32f2f;
                            margin-bottom: 12px;
                        }

                        p {
                            color: #666;
                            margin-bottom: 20px;
                        }

                        a {
                            display: inline-block;
                            padding: 12px 25px;
                            background: #8b5e34;
                            color: white;
                            text-decoration: none;
                            border-radius: 8px;
                        }

                    </style>

                </head>

                <body>

                    <div class="box">

                        <h2>
                            Access Denied ❌
                        </h2>

                        <p>
                            You are not authorized
                            to access the Admin Dashboard.
                        </p>

                        <a href="/">
                            Go to Home
                        </a>

                    </div>

                </body>

                </html>
            """, 403


        # ==========================================
        # TOTAL BLOCKED DATES
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM blocked_dates
        """)

        total_blocked = cursor.fetchone()["total"]


        # ==========================================
        # TOTAL USERS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users
        """)

        total_users = cursor.fetchone()["total"]


        # ==========================================
        # GET BLOCKED DATES
        # ==========================================

        cursor.execute("""
            SELECT
                id,
                blocked_date,
                reason
            FROM blocked_dates
            ORDER BY blocked_date ASC
        """)

        blocked_dates = cursor.fetchall()


        # ==========================================
        # OPEN ADMIN PAGE
        # ==========================================

        return render_template(
            "admin.html",
            total_blocked=total_blocked,
            total_users=total_users,
            blocked_dates=blocked_dates
        )


    finally:

        cursor.close()
        connection.close()

# ==========================================
# ADMIN - BLOCK DATE
# ==========================================

@app.route(
    "/admin/block-date",
    methods=["POST"]
)
def block_date():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_id" not in session:

        return redirect("/login")


    # ==========================================
    # CHECK ADMIN
    # ==========================================

    if session.get("user_role") != "admin":

        return "Access Denied ❌", 403


    blocked_date = request.form.get(
        "blocked_date"
    )


    reason = request.form.get(
        "reason",
        ""
    )


    # ==========================================
    # CHECK DATE
    # ==========================================

    if not blocked_date:

        flash(
            "Please select a date.",
            "error"
        )

        return redirect("/admin")


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        # ==========================================
        # INSERT BLOCKED DATE
        # ==========================================

        query = """
            INSERT INTO blocked_dates
            (
                blocked_date,
                reason
            )
            VALUES
            (
                %s,
                %s
            )
        """


        cursor.execute(
            query,
            (
                blocked_date,
                reason
            )
        )


        connection.commit()


        flash(
            "Date blocked successfully! 🚫",
            "success"
        )


    except mysql.connector.IntegrityError:

        flash(
            "This date is already blocked! ⚠️",
            "error"
        )


    finally:

        cursor.close()
        connection.close()


    return redirect("/admin")


# ==========================================
# ADMIN - REMOVE BLOCKED DATE
# ==========================================

@app.route(
    "/admin/unblock-date/<int:block_id>",
    methods=["POST"]
)
def unblock_date(block_id):

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_id" not in session:

        return redirect("/login")


    # ==========================================
    # CHECK ADMIN
    # ==========================================

    if session.get("user_role") != "admin":

        return "Access Denied ❌", 403


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        # ==========================================
        # DELETE BLOCKED DATE
        # ==========================================

        query = """
            DELETE FROM blocked_dates
            WHERE id = %s
        """


        cursor.execute(
            query,
            (block_id,)
        )


        connection.commit()


        flash(
            "Date is available again! ✅",
            "success"
        )


    finally:

        cursor.close()
        connection.close()


    return redirect("/admin")


# ==========================================
# TEST DATABASE
# ==========================================

@app.route("/test-db")
def test_db():

    connection = get_db_connection()


    if connection.is_connected():

        connection.close()

        return """
            Database connected successfully! ✅
        """


    return """
        Database connection failed ❌
    """


# ==========================================
# RUN FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )