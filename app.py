import streamlit as st
import pickle
import numpy as np
import pandas as pd

from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load the trained model
with open('delivery_model.pickle', 'rb') as model_file:
    model = pickle.load(model_file)

# Load the label mappings
label_mappings = {
    'Festival': {'No ': 1, 'Yes ': 2, 'NaN ': 0},
    'Weatherconditions': {'Sunny': 5, 'Stormy': 4, 'Sandstorms': 3, 'Cloudy': 0, 'Fog': 1, 'Windy': 6, 'NaN': 2},
    'Road_traffic_density': {'High ': 0, 'Jam ': 1, 'Low ': 2, 'Medium ': 3, 'NaN ': 4},
    'Type_of_vehicle': {'motorcycle ': 2, 'scooter ': 3, 'electric_scooter ': 1, 'bicycle ': 0},
    'City': {'Urban ': 3, 'Metropolitian ': 0, 'Semi-Urban ': 2, 'NaN ': 1},
    'Vehicle_condition': {0: '0', 1: '1', 2: '2', 3: '3'}
}

# Function to preprocess input data
def preprocess_input(input_data):
    # Map categorical features to their encoded values
    for feature, mapping in label_mappings.items():
        input_data[feature] = input_data[feature].map(mapping)
    
    # Convert DataFrame to NumPy array
    input_features = input_data.values
    
    return input_features

# Streamlit app
def main():
    st.title("Delivery Time Predictor with Email and SMS Notification")

    Id = st.text_input("Product ID")
    name = st.text_input("Customer Name")
    age = st.number_input("Delivery person's Age", min_value=18, max_value=100, value=30)
    ratings = st.number_input("Delivery person's Ratings", min_value=1.0, max_value=5.0, value=4.0)
    distance = st.number_input("Distance (in km)", min_value=0.1, max_value=100.0, value=5.0)
    packaging_time = st.number_input("Shipping Time (in mins)", min_value=0.0, max_value=60.0, value=10.0)
    festival = st.selectbox("Festival", list(label_mappings['Festival'].keys()))
    weather = st.selectbox("Weather Conditions", list(label_mappings['Weatherconditions'].keys()))
    traffic = st.selectbox("Road Traffic Density", list(label_mappings['Road_traffic_density'].keys()))
    vehicle_type = st.selectbox("Type of Vehicle", list(label_mappings['Type_of_vehicle'].keys()))
    city = st.selectbox("City", list(label_mappings['City'].keys()))
    multiple_deliveries = st.number_input("Multiple Deliveries (0 for No, 1 for Yes)", min_value=0, max_value=1, value=0)
    vehicle_condition = st.selectbox("Vehicle Condition", [0, 1, 2, 3])
    email_input = st.text_input("Enter Customer email address")
    phone_input = st.text_input("Enter Customer phone number (with country code)")

    if st.button("Predict"):
        input_dict = {
            'Delivery_person_Age': age,
            'Delivery_person_Ratings': ratings,
            'distance': distance,
            'Packaging_time_difference': packaging_time,
            'Festival': festival,
            'Weatherconditions': weather,
            'Road_traffic_density': traffic,
            'Type_of_vehicle': vehicle_type,
            'City': city,
            'multiple_deliveries': multiple_deliveries,
            'Vehicle_condition': vehicle_condition
        }
        
        input_df = pd.DataFrame([input_dict])
        input_features = preprocess_input(input_df)
        
        prediction = model.predict(input_features)

        send_email(email_input, prediction,Id,name)
        send_sms(phone_input, prediction,Id,name)
        st.success(f"Predicted Delivery Time: {prediction[0]:.2f} minutes")

def send_email(email, predicted_delivery_time,Id,name):
    # Your email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "omgoswami.1102@gmail.com"
    sender_password = "create_it"

    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Expected Delivery Time"

    # Email body
    body = f"Hello {name},\nYour Product Id is : {Id} And\nYour expected delivery time is: {predicted_delivery_time} minutes."
    message.attach(MIMEText(body, "plain"))

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())

def send_sms(phone_number, predicted_delivery_time,Id,name):
    # Your Twilio account SID and auth token
    twilio_account_sid = "Not_Shared"
    twilio_auth_token = "Not_shared"

    # Initialize Twilio client
    client = Client(twilio_account_sid, twilio_auth_token)

    # Send SMS message
    message = f"Hello {name},\nYour Product Id is : {Id} And \nYour expected delivery time is: {predicted_delivery_time} minutes."
    client.messages.create(
        to=str(phone_number),
        from_="+1234",
        body=message
    )

if __name__ == '__main__':
    main()
