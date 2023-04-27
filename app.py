import json
import numpy as np
import streamlit as st
from keras.utils import load_img
import requests
from keras.applications import VGG16
from PIL import Image
from streamlit_option_menu import option_menu
from pymongo import MongoClient
import io
import random
from keras import models
import cv2

# Connect to MongoDB
client = MongoClient("mongodb+srv://shriganeshbhandari09:Password@cluster0.gsp5vho.mongodb.net/?retryWrites=true&w=majority")
db = client["Demo"]
collection = db["Signatures"]



st.set_page_config(layout="centered", page_icon="📑", page_title="Siganture Forgery Detection")


selected = option_menu(
    menu_title=None,
    options= ["Home","Program","Registration"],
    icons=["house","robot","file-person"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)


def set_bg_hack_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(https://www.rhbgroup.com/~/media/images/laos/about-us/our-people/profile-bg.ashx?h=745&la=en&w=480);
             background-repeat: no-repeat;
             background-size: 1250px 1120px;
             background-position: center;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
set_bg_hack_url()



# load the saved model
model = models.load_model('signature_data_one_shot/signature_model')

# define the function for signature forgery recognition
def check_forgery(path_img_1, path_img_2):
    img1 = cv2.imread(path_img_1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(path_img_2, cv2.IMREAD_GRAYSCALE)
    width = 650
    height = 268
    dim = (width, height)

    # resize image
    img1 = cv2.resize(img1, dim, interpolation = cv2.INTER_AREA)
    img2 = cv2.resize(img2, dim, interpolation = cv2.INTER_AREA)
    st.image([img1, img2], caption=['Signature 1', 'Signature 2'], width=200)
    img1 = img1.reshape((1, 268, 650, 1))
    img2 = img2.reshape((1, 268, 650, 1))
    img1 = img1.astype('float32') / 255
    img2 = img2.astype('float32') / 255

    if model.predict((img1, img2))[0][0] >=0.5:
        return 'Genuine Signatures'
    else:
        return 'Forged Signatures'

if selected =="Home":
    st.header(" Why a signature forgery detection tool is needed ?")
    st.write(  '''Currently we have entered the digital area, but there are still many customers or customers who still use their signature as the main form of authentication for various transactions.
    Their signatures certify checks, new account documents, loan documents, and more, and to minimize fraud risk, banks need the right solution to detect counterfeiting quickly and accurately.''')
    st.header(" Types of signature forgery  ?")
    st.write("There are several types of signature forgery")
    st.subheader("Baseless falsification")
    st.write(''' These fake signatures bear little or no resemblance to the customer's actual signature because the forger has no access to the signature.
    For example, thieves open new accounts using stolen Social Security Numbers they buy from the dark web or if they write checks from stolen checkbooks.'''
    )
    st.subheader("Basic forgery")
    st.write(''' Also known as unskilled forgeries, these fakes are created by tracing an actual signature.
    They tend to look very similar to actual signatures and the differences are often undetectable to the human eye alone.
    However, they focus on accuracy rather than fluency.
    '''
    )
    st.subheader("Professional Counterfeit")
    st.write(''' The most difficult type of counterfeiting to detect,
    these signatures are created by criminals who have spent a great deal of time practicing and have the ability to mimic actual signatures in a way that looks accurate and relatively fluent to the naked eye.
    
    source: https://sqnbankingsystems.com/blog/how-to-improve-forgery-detection-at-your-financial-institution/   
    '''
    )

if selected =="Program":
    st.header("Handwritten Signature Forgery Detection")
    account_number_to_view = st.text_input('Enter the Customer Account Number',value="",help='input without periods(.), commas(,), or dashes(-), such as: 00000001',max_chars=10)   
    if (account_number_to_view ==""):
       st.write("Enter your Account Number")
    else:
       try:
            user_data = collection.find_one({"account_number": account_number_to_view})
            if user_data is not None:
                st.write("Name:", user_data["name"])
                st.write("Email ID:", user_data["email"])
                st.write("Account Number:", user_data["account_number"])
                signatures = user_data["signatures"]
            if len(signatures) > 0:
                image1=load_img(io.BytesIO(signatures[0]))
                st.image(image1) 
            else:
                st.write("No signatures found for the given account number.")
            
       except :
            st.markdown('Do not have an account yet? register on the **Registration** Tab')
            st.error('Account not found, please enter a valid number !')
        

    uploaded_files_0 = st.file_uploader(f"Upload the Customer's signature {account_number_to_view}", type=['jpg','png','jpeg']) 
    if uploaded_files_0 is not None:
        st.image(uploaded_files_0)  
        
    if st.button ('Predict'):
        if len(signatures) > 0 and uploaded_files_0 is not None:
            img1 = cv2.imdecode(np.frombuffer(signatures[0], np.uint8), cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imdecode(np.frombuffer(uploaded_files_0.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
            width = 650
            height = 268
            dim = (width, height)

            # resize image
            img1 = cv2.resize(img1, dim, interpolation=cv2.INTER_AREA)
            img2 = cv2.resize(img2, dim, interpolation=cv2.INTER_AREA)
            img1 = img1.reshape((1, 268, 650, 1))
            img2 = img2.reshape((1, 268, 650, 1))
            img1 = img1.astype('float32') / 255
            img2 = img2.astype('float32') / 255
            result = model.predict([img1, img2])
            diff = result[0][0]
            st.write("Difference Score", diff)
            if model.predict((img1, img2))[0][0] >= 0.5:
                st.subheader('Genuine Signatures')
            else:
                st.subheader('Forged Signatures')
        else:
            st.subheader('Please upload the customer signature and ensure the account number is valid.') 
        

def is_email_registered(email, account_number):
    user = collection.find_one({"$or": [{"email": email}, {"account_number": account_number}]})
    return user is not None


if selected =="Registration":
    st.title("Customer signature registration")
    st.subheader(" Enter the customer's personal data ")
    #st.subheader("Upload Signatures")
    name = st.text_input("Name:")
    email = st.text_input("Email ID:")
    account_number = st.text_input('Account Number:',value="",help='input without periods(.), commas(,), or dashes(-), such as: 0000000001',max_chars=10)
    signatures = st.file_uploader("Upload signatures (PNG format only)", accept_multiple_files=True)

    # Save user data and signatures to MongoDB when the user clicks the submit button
    if st.button("Submit"):
        if is_email_registered(email, account_number):
            st.warning("Account number is already registered")
        else:
            signature_data = []
            for signature in signatures:
                if len(signature_data) >= 5:
                    break
                signature_bytes = io.BytesIO(signature.read())
                signature_data.append(signature_bytes.getvalue())
            user_data = {
                "name": name,
                "email": email,
                "account_number": account_number,
                "signatures": signature_data
            }
            collection.insert_one(user_data)
            st.subheader("Signatures uploaded successfully.")
       

