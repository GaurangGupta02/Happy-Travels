from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import pymongo
from xhtml2pdf import pisa
from bson import ObjectId  
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__, template_folder='C:\\Users\\Gaurang\\Desktop\\happytravels\\template')
app.secret_key = "your_secret_key"  # Secret key for flashing messages
app.config['SESSION_TYPE'] = 'filesystem'

# Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")  # Use your MongoDB URI here
    db = client['travel']  # Database name
    collection = db['customer_records']  # Collection name
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Utility function to convert ObjectId fields to strings
def convert_object_id(data):
    """Convert all ObjectId fields in a dictionary to strings."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, dict):  # Recursively convert nested dictionaries
                convert_object_id(value)
    return data

# Define route for the home page (root URL)
@app.route('/')
def home():
    return render_template('home.html')  # Render the home page

# Define route for the booking form
@app.route('/booking', methods=['GET', 'POST'])
def booking_form():
    if request.method == 'POST':
        # Extract form data
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

        # Insert into MongoDB and convert ObjectId to string
        inserted_id = collection.insert_one(customer_data).inserted_id
        customer_data['_id'] = str(inserted_id)  # Convert the ObjectId to string

        # Store the customer data in session for use in the PDF generation
        session['customer_data'] = customer_data

        # Flash a success message
        flash(f"Booking Confirmed for {customer_data['name']}!")
        return redirect(url_for('success'))  # Redirect to success route

    return render_template('booking_form.html')  # Ensure this file is in the templates folder

# Define route for the success page
@app.route('/success')
def success():
    return render_template('success.html')  # Render the success page template

# Define route to generate and download the PDF receipt
@app.route('/generate_receipt')
def generate_receipt():
    if 'customer_data' in session:
        customer_data = session['customer_data']

        # Generate the PDF file for the booking receipt
        rendered_html = render_template('generate_receipt.html', customer_data=customer_data)
        pdf_path = f"{customer_data['name']}_booking_receipt.pdf"
        
        # Generate PDF and save to file
        with open(pdf_path, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_file)

        if pisa_status.err:
            flash("Failed to generate the PDF receipt.")
            return redirect(url_for('success'))

        # Send the generated PDF as a downloadable file
        return send_file(pdf_path, as_attachment=True)
    else:
        flash("No booking information available.")
        return redirect(url_for('home'))

# Define route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')  # Render the contact page template

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
