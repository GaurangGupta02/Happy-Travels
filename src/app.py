from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import pymongo
from xhtml2pdf import pisa
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv  # Import dotenv
from .other_module import some_function

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='C:\\Users\\Gaurang\\Desktop\\happytravels\\src\\template')
app.secret_key = "your_secret_key"  # Secret key for flashing messages
app.config['SESSION_TYPE'] = 'filesystem'
# MongoDB configuration
MONGO_URI = os.getenv("mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("travel")
COLLECTION_NAME = os.getenv("customer_records")

# Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["travel"]
    collection = db["customer_records"]
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Utility function to convert ObjectId fields to strings
def convert_object_id(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, dict):
                convert_object_id(value)
    return data

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Booking form route
@app.route('/booking', methods=['GET', 'POST'])
def booking_form():
    if request.method == 'POST':
        customer_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'email': request.form['email'],
            'gender': request.form['gender'],
            'age': request.form['age'],
            'payment': request.form['payment'],
            'meal_preference': request.form['meal_preference'],
            'rating': request.form['rating']
        }

        inserted_id = collection.insert_one(customer_data).inserted_id
        customer_data['_id'] = str(inserted_id)

        session['customer_data'] = customer_data

        flash(f"Booking Confirmed for {customer_data['name']}!")
        return redirect(url_for('success'))

    return render_template('booking_form.html')

# Success route
@app.route('/success')
def success():
    return render_template('success.html')

# Generate PDF receipt route
@app.route('/generate_receipt')
def generate_receipt():
    if 'customer_data' in session:
        customer_data = session['customer_data']

        rendered_html = render_template('generate_receipt.html', customer_data=customer_data)
        pdf_path = secure_filename(f"{customer_data['name']}_booking_receipt.pdf")
        
        with open(pdf_path, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_file)

        if pisa_status.err:
            flash("Failed to generate the PDF receipt.")
            return redirect(url_for('success'))

        return send_file(pdf_path, as_attachment=True)
    else:
        flash("No booking information available.")
        return redirect(url_for('home'))

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
