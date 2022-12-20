# Author: Kwa Chin Soon
# Nov 2022

import streamlit as st
# other libs
import numpy as np
import pandas as pd
import pickle
# import pyautogui # for reset button: pip install pyautogui

# load the model.pkl
path = r'C:/Users/kwach/OneDrive/Desktop/Workshop/model.pkl'
with open('model.pkl', "rb") as f:
	model = pickle.load(f)

# Streamlit provides a caching mechanism that allows your app to stay performant 
# even when loading data from the web, manipulating large datasets, 
# or performing expensive computations. This is done with the @st.cache decorator.
@st.cache()

def prediction(age, incomeK, HHsize, kids, Month, transaction, amount):
	# Making predictions
	prediction = model.predict([[age, incomeK, HHsize, kids, Month, transaction, amount]])
	if prediction == 0:
		pred = 'Not Attrited'
	else:
		pred = 'Attrited'
	return pred


# putting the app related codes in main()
def main():
	# -- Set page config
	apptitle = 'DSSI'
	st.set_page_config(page_title=apptitle, page_icon='random', 
		layout= 'wide', initial_sidebar_state="expanded")
	# random icons in the browser tab

	# give a title to your app
	st.title('Solution Implementation')
	#front end elements of the web page 
	# pick colors from: https://www.w3schools.com/tags/ref_colornames.asp
	html_temp = """ <div style ="background-color:AntiqueWhite;padding:15px"> 
       <h1 style ="color:black;text-align:center;">A customer attrition assessment app</h1> 
       </div> <br/>"""

    #display the front end aspect
	st.markdown(html_temp, unsafe_allow_html = True)
	# let us make infrastructure to provide inputs
	# we will add the inputs to side bar
	st.sidebar.info('Provide input using the panel')
	st.info('Click Assess button below')

	age = st.sidebar.slider('age', 21, 75, 30)
	st.write('input age', age)
	incomeK = st.sidebar.slider('Income in 1000s', 8, 300, 120)
	st.write('input income in 000', incomeK*1000)
	HHsize = st.sidebar.slider('household size', 1, 6, 2)
	st.write('input household size', HHsize)
	kids = st.sidebar.slider('kids', 0, 3, 1)
	st.write('input no.of kids', kids)
	Month = st.sidebar.slider('Month', 1, 24, 12)
	st.write('Month', Month)
	transaction = st.sidebar.slider('transaction', 0, 500, 50)
	st.write('transaction', transaction)
	amount = st.sidebar.slider('amount', 0, 3000, 1500)
	st.write('amount', amount)

	result =""
	# assessment button
	if st.button("Predict"):
		assessment = prediction(age, incomeK, HHsize, kids, Month, transaction, amount)
		st.success('**System assessment says:** {}'.format(assessment))

	# if st.button("Reset"):
	# 	pyautogui.hotkey("ctrl","F5")

	# st.balloons()
	st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.

if __name__ == '__main__':
	main()
