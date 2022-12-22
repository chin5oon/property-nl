# Author: Kwa Chin Soon
# Nov 2022

import streamlit as st
import datetime
# other libs
import numpy as np
import pandas as pd
import pickle

# import pyautogui # for reset button: pip install pyautogui


# Streamlit provides a caching mechanism that allows your app to stay performant 
# even when loading data from the web, manipulating large datasets, 
# or performing expensive computations. This is done with the @st.cache decorator.
@st.cache()

def prediction(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
          level, maxlevel, area, district):
    
    if district == 6:
        pred = "No suitable model to assess."
    else:
        # Pre-processing user input  
        
        rh = level / maxlevel
        
    	# Making predictions
        
        file2 =  str(district) + "_epmodel.pkl"
        path = file2
        with open(path, "rb") as f:
            epmodel = pickle.load(f)
        
        prediction = epmodel.predict([[age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                  level, rh, area]])
    
        if prediction == 0:
            pred = 'Do not buy. Expected Profit less than 20% in 3 years.'
        else:
            pred = 'Buy. Expected Profit more than 20% in 3 years.'
    return pred

def price(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
          level, maxlevel, district):
    
    newsale = 0
    resale = 1
    subsale = 0
    
    rh = level / maxlevel
    
	# Making predictions

    file =  str(district) + "_ensemble_model.pkl"
    path = file
    with open(path, "rb") as f:
        model = pickle.load(f)
    
    p = model.predict([[age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                      level, rh, district, newsale, resale, subsale]])
    
    if district == 10 or district == 12: 
        p = np.expm1(p)
    else:
        p = p
        
    return p


# putting the app related codes in main()
def main():
    # -- Set page config
    apptitle = 'Non-Landed Properties in Singapore'
    st.set_page_config(page_title=apptitle, page_icon='random', 
                       layout= 'wide', initial_sidebar_state="expanded")
    # random icons in the browser tab

    # give a title to your app
    st.title('Should you buy the property?')
    #front end elements of the web page 
    # pick colors from: https://www.w3schools.com/tags/ref_colornames.asp
    html_temp = """ <div style ="background-color:AntiqueWhite;padding:15px"> 
       <h1 style ="color:black;text-align:center;">A property price estimation 
       and evaluation app</h1> 
       </div> <br/>"""

    #load file
    df = pd.read_csv('transactions_full_median.csv')
    #drop ENBLOC
    df = df[((df['ENBLOC'] == 0))]
    
    #Calculate age of property when transaction took place
    df.loc[((df['Completion Year'] == "Uncompleted")) , 'Completion Year'] = df['year']
    
    df['Completion Year'] = df['Completion Year'].apply(pd.to_numeric)
    df['year'] = df['year'].apply(pd.to_numeric)

    
    #Tenure Type: Freehold/999 yr = 1, 99-yr = 0
    
    df.loc[((df['TenureType_Ind'] == "999-yr")) , 'TenureType_Ind'] = 1
    df.loc[((df['TenureType_Ind'] == "Freehold")) , 'TenureType_Ind'] = 1
    df.loc[((df['TenureType_Ind'] == "99-yr")) , 'TenureType_Ind'] = 0


    #Split dataset into non-landed

    df_nl = df[~((df['Property.Type'] == 'Detached House'))]
    df_nl = df_nl[~((df_nl['Property.Type'] == 'Semi-Detached House'))] 
    df_nl = df_nl[~((df_nl['Property.Type'] == 'Terrace House'))] 

    project_list = df_nl['Project.Name'].unique().tolist()
    
    #display the front end aspect
    st.markdown(html_temp, unsafe_allow_html = True)
    # let us make infrastructure to provide inputs
    # we will add the inputs to side bar
    st.sidebar.info('Provide input using the panel')
    st.info('Click Assess button below')
 
    choice = st.sidebar.radio('How do you want to input', ("By Project Name", "By Manual Input"))
    
    if choice == "By Project Name":
        proj = st.sidebar.selectbox("Choose the project:", project_list)
        st.write("You selected:", proj)
        df1 = df_nl[df_nl['Project.Name'] == proj]
        district = df1["Postal.District"].mode()
        age_at_sale = datetime.date.today().year - df1["Completion Year"].max()
        Dist_Sch_Label = df1["Dist_Sch_Label"].mode()
        sch = df1["Nearest Sch"].mode()
        Distance_MRTexit = df1["Distance_Stn"].mode()
        stn = df1["Nearest Stn"].mode()
        TenureType_Ind = df1["TenureType_Ind"].mode()
        maxlevel = df1["maxLevel"].mode()
        
        st.write('District', district.values[0])
        st.write('age at sale', age_at_sale)
        st.write('Sch Label', Dist_Sch_Label.values[0], "(", sch.values[0], ")")
        st.write('Distance from MRT (km)', Distance_MRTexit.values[0], "(", stn.values[0], ")")
        st.write('Tenure Type', TenureType_Ind.values[0])
        st.write('Maximum level of development', maxlevel.values[0])
        
        df1 = df1[["Date", "Address", "Avg area sqf", "Transacted.Price....", "Type.of.Sale"]]

        
    else:
        district = st.sidebar.selectbox('District', ([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
                                              16,17,18,19,20,21,22,23,25,26,27,28]))
  
        age_at_sale = st.sidebar.slider('Age at Sale', 0, 100, 25)
        st.write('District', district)
        st.write('age at sale', age_at_sale)
        
        Dist_Sch_Label = st.sidebar.radio(
            'School label: less than 1KM input 1; between 1KM to 2KM input 2; more than 2KM input 3',
            (1, 2, 3))
        st.write('Sch Label', Dist_Sch_Label)
        Distance_MRTexit = st.sidebar.slider('Distance from MRT (km)', 0, 30, 2)
        st.write('Distance from MRT (km)', Distance_MRTexit)
        TenureType_Ind = st.sidebar.radio('Tenure Type: 99-yr input 0; 999-yr or freehold input 1',
                                  (0,1))  
        st.write('Tenure Type', TenureType_Ind)
        maxlevel = st.sidebar.slider('Maximum level of development', 1, 70, 20)
        st.write('Maximum level of development', maxlevel)
    
    level = st.sidebar.slider('Level', 1, 70, 15)
    st.write('Level', level)
    
    area = st.sidebar.text_input('Area (square feet)', 1150)
    area = float(area)
    district = int(district)
    #age_at_sale = int(age_at_sale)
    #Distance_MRTexit = int(Distance_MRTexit)
    TenureType_Ind = int(TenureType_Ind)
    maxlevel = int(maxlevel)
    st.write('Area (square feet)', area)
    
    
    # assessment button
    if st.button("Assess"):
        est_price = price(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                  level, maxlevel, district) * area
        est_price = int(est_price)
        est_price = '{:,.2f}'.format(est_price)
        st.success('**System assessment says:** Price is estimated to be: ${}'.format(est_price))
        assessment = prediction(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                                level, maxlevel, area, district)
        st.success('**System assessment says:** {}'.format(assessment))

    # if st.button("Reset"):
    # 	pyautogui.hotkey("ctrl","F5")

    # st.balloons()
    
    if choice == "By Project Name":
        df1["Date"] = df1["Date"].astype('datetime64[ns]')
        df1 = df1.sort_values(by = ['Date'], ascending = False)
        df1
        st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.
    else:
        st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.
        
if __name__ == '__main__':
	main()
