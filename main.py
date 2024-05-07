# Importing the required packages
import streamlit as st
import pandas as pd
import math as m
import smtplib, csv
from email.message import EmailMessage

sender = "abc@gmail.com" #enter sender email
password = "abc"         #enter passwd for above mail

def topsis(inputFileName, weights, impacts):

    # Reading the input csv file
    dataset = pd.read_csv(inputFileName)

    # Dropping and NULL values
    dataset.dropna(inplace = True)

    # Dropping categorical values and using only numerical values
    df = dataset.iloc[0:,1:].values

    # Converting the dataset into a matrix
    mat = pd.DataFrame(df)

    # Calculating root of sum of square for each column
    rootOfSumOfSquares = []
    for col in range(0, len(mat.columns)):
        sum = 0
        colValues = mat.iloc[0:,[col]].values
        for val in colValues:
            sum = sum + m.pow(val,2)
        rootOfSumOfSquares.append(m.sqrt(sum))
    
    # Dividing every matrix value with its corresponding column rootOfSumOfSquares value to get Normalized Performance Value
    k = 0
    while(k<len(mat.columns)):
        for j in range(0,len(mat)):
            mat[k][j] = mat[k][j]/rootOfSumOfSquares[k]
        k = k+1

    # Multiplying each of the matrix value with its corresponding column weight to get Weighted Normalized Decision Matrix
    k = 0
    while(k<len(mat.columns)):
        for j in range(0,len(mat)):
            mat[k][j] = mat[k][j]*weights[k]
        k = k+1

    # Finding the ideal best and worst values for each column according to the impact of that column
    idealBestValue = []
    idealWorstValue = []
    for col in range(0, len(mat.columns)):
        colValues = mat.iloc[0:,[col]].values

        if impacts[col]=='+':
            maxVal = max(colValues)
            minVal = min(colValues)
            idealBestValue.append(maxVal)
            idealWorstValue.append(minVal)

        if impacts[col]=='-':
            maxVal = max(colValues)
            minVal = min(colValues)
            idealBestValue.append(minVal)
            idealWorstValue.append(maxVal)

    # Calculating the Euclidean Distance from ideal best and ideal worst values for each row     
    SiPlus = []
    SiMinus = []
    for row in range(0, len(mat)):
        rowValues = mat.iloc[row, 0:].values
        temp1 = 0
        temp2 = 0
        for val in range(0, len(rowValues)):
            temp1 = temp1 + m.pow(rowValues[val]-idealBestValue[val],2)
            temp2 = temp2 + m.pow(rowValues[val]-idealWorstValue[val],2)
        SiPlus.append(m.sqrt(temp1))
        SiMinus.append(m.sqrt(temp2))

    # Calculating the Performance Score for each row
    Pi = []
    for row in range(0, len(mat)):
        Pi.append(SiMinus[row]/(SiMinus[row]+SiPlus[row]))

    # Assigning Rank
    Rank = []
    sortPi = sorted(Pi, reverse=True)
    for row in range(0, len(mat)):
        for i in range(0, len(sortPi)):
            if Pi[row] == sortPi[i]:
                Rank.append(i+1)

    # Appending the new columns to original matrix
    col1 = dataset.iloc[:,[0]].values
    mat.insert(0, dataset.columns[0], col1)
    mat['TOPSIS Score'] = Pi
    mat['Rank'] = Rank

    return mat

st.set_page_config(layout='centered', page_title='Topsis Calculator')
st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
st.header("Topsis Calculator for MCDM")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer:before {content: 'Made by Riya'; display:block; position:relative;color:tomato;}
            footer {visibility: visible;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
with st.form("form1", clear_on_submit=True):
    inputFileName = st.file_uploader("Input File Name")
    weights = st.text_input("Weights")
    impacts = st.text_input("Impacts")
    email = st.text_input("Email ID", placeholder='rriya_be20@thapar.edu')
    submit = st.form_submit_button("Submit")

def checkFormat(w):
    for i in range(1, len(w), 2):
        if w[i] == ',':
            continue
        else:
            return False
    return True

subject = "Results"
msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = email
message = """This is the result file of the input file provided by you after topsis calculation.
Done By -
Riya
"""
filename = "results.csv"
if submit is True:
    if(len(weights)==len(impacts)):
        weights = weights.split(',') if checkFormat(weights) == True else None
        if weights != None:
            for i in range(0, len(weights)):
                weights[i] = int(weights[i])
        else:
            st.write("Weights are not comma separated!")
            exit()
        impacts = impacts.split(',') if checkFormat(impacts) == True else None

        count = 0
        if impacts != None:
            for i in range(0, len(impacts)):
                if(impacts[i]=='+' or impacts[i]=='-'):
                    count = count+1
            if count==len(impacts):
                pass
            else:
                st.write("Impacts must be +ve or -ve!")
                exit()
        else:
            st.write("Impacts are not comma separated!")
            exit()
        csvfile = topsis(inputFileName ,weights, impacts)       

        with open(filename, 'w') as csvfiles: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfiles) 
                
            # writing the fields 
            csvwriter.writerow(list(csvfile.columns)) 
                
            # writing the data rows 
            file_data = csvwriter.writerows(list(csvfile.values.tolist()))
        
        with open(filename,"rb") as f:
                file_data = f.read()
                file_name = f.name
                msg.set_content(message)
                msg.add_attachment(file_data,maintype="application",subtype="csv",filename=file_name)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                try:
                    server.login(sender, password)
                    server.send_message(msg)
                    st.write("Email Sent Successfully!")
                except smtplib.SMTPAuthenticationError:
                    print("Unable to sign in")
    else:
        st.write("Number of Impacts and Weights should be equal!")