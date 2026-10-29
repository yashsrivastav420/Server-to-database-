
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from mysql.connector import Error

# --------------------------------------------------
# 1. Project setup
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Load database settings from the .env file
load_dotenv(BASE_DIR / ".env", override=True)

# Create Flask application
app = Flask(__name__)


# --------------------------------------------------
# 2. Homepage
# --------------------------------------------------

@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# --------------------------------------------------
# 3. CSS file
# --------------------------------------------------

@app.get("/style.css")
def styles():
    return send_from_directory(BASE_DIR, "style.css")


# --------------------------------------------------
# 4. JavaScript file
# --------------------------------------------------

@app.get("/script.js")
def scripts():
    return send_from_directory(BASE_DIR, "script.js")


# --------------------------------------------------
# 5. Contact form API
# --------------------------------------------------

@app.post("/api/contact")
def save_contact():

    # Read JSON data sent by the frontend
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request data."
        }), 400

    # Extract submitted values
    full_name = data.get("full_name", "")
    email = data.get("email", "")
    company = data.get("company", "")
    purpose = data.get("purpose", "")
    message = data.get("message", "")

    # Ensure all fields contain strings
    if not all(
        isinstance(value, str)
        for value in [
            full_name,
            email,
            company,
            purpose,
            message
        ]
    ):
        return jsonify({
            "error": "Invalid field values."
        }), 400

    # Remove extra spaces
    full_name = full_name.strip()
    email = email.strip()
    company = company.strip()
    purpose = purpose.strip()
    message = message.strip()

    # Validate required fields
    if not all([full_name, email, purpose, message]):
        return jsonify({
            "error": "Please complete all required fields."
        }), 400

    # Validate field lengths
    if len(full_name) > 100 or len(email) > 150:
        return jsonify({
            "error": "Name or email is too long."
        }), 400

    if len(company) > 150 or len(purpose) > 50:
        return jsonify({
            "error": "A field is too long."
        }), 400

    # Basic email and message validation
    if len(message) > 10000 or "@" not in email:
        return jsonify({
            "error": "Please check your details."
        }), 400

    connection = None
    cursor = None

    try:
        # Connect Python to MySQL
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "yash_portfolio"),
            connection_timeout=10
        )

        # Create a cursor for SQL commands
        cursor = connection.cursor()

        # SQL query to save the enquiry
        sql = """
            INSERT INTO contact_enquiries
                (full_name, email, company, purpose, message)
            VALUES (%s, %s, %s, %s, %s)
        """

        # Values are parameterized to prevent SQL injection
        values = (
            full_name,
            email,
            company or None,
            purpose,
            message
        )

        # Execute query and save the record
        cursor.execute(sql, values)
        connection.commit()

        return jsonify({
            "message": "Thank you! Your enquiry has been submitted."
        }), 201

    except (Error, ValueError) as e:
        # Show the real error in the VS Code terminal
        print("DATABASE ERROR:", repr(e))
        app.logger.exception("Failed to save contact enquiry.")

        return jsonify({
            "error": "Unable to save your enquiry right now."
        }), 500

    except Exception as e:
        # Log unexpected errors without exposing details to visitors
        print("UNEXPECTED ERROR:", repr(e))
        app.logger.exception("Unexpected error while saving enquiry.")

        return jsonify({
            "error": "Unable to save your enquiry right now."
        }), 500

    finally:
        # Close the cursor safely
        if cursor is not None:
            cursor.close()

        # Close the connection safely
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# 6. Start Flask
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
