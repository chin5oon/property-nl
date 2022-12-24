# Author: Kwa Chin Soon
# Nov 2022

import streamlit as st
import datetime
# other libs
import numpy as np
import pandas as pd
import pickle
import altair as alt

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
    apptitle = 'Properties in Singapore'
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
    m = pd.read_csv('nl_resale_median_district.csv')
    l = pd.read_csv('transactions_full_landed.csv')

    #Calculate age of property when transaction took place
    df.loc[((df['Completion Year'] == "Uncompleted")) , 'Completion Year'] = df['year']
    
    df['Completion Year'] = df['Completion Year'].apply(pd.to_numeric)
    df['year'] = df['year'].apply(pd.to_numeric)

    
    #Tenure Type: Freehold/999 yr = 1, 99-yr = 0
    
    df.loc[((df['TenureType_Ind'] == "999-yr")) , 'TenureType_Ind'] = 1
    df.loc[((df['TenureType_Ind'] == "Freehold")) , 'TenureType_Ind'] = 1
    df.loc[((df['TenureType_Ind'] == "99-yr")) , 'TenureType_Ind'] = 0
    
    #Calculate age of property when transaction took place
    l.loc[((l['Completion Year'] == "Uncompleted")) , 'Completion Year'] = l['year']
    
    l['Completion Year'] = l['Completion Year'].apply(pd.to_numeric)
    l['year'] = l['year'].apply(pd.to_numeric)

    
    #Tenure Type: Freehold/999 yr = 1, 99-yr = 0
    
    l.loc[((l['TenureType_Ind'] == "999-yr")) , 'TenureType_Ind'] = 1
    l.loc[((l['TenureType_Ind'] == "Freehold")) , 'TenureType_Ind'] = 1
    l.loc[((l['TenureType_Ind'] == "99-yr")) , 'TenureType_Ind'] = 0    
    
    nonlanded = df['Project.Name'].unique().tolist()
    landed = l['Project.Name'].unique().tolist()
    project_list = nonlanded + landed 
    df_nl = df
    
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
        if proj in nonlanded:
            df1 = df_nl[df_nl['Project.Name'] == proj]
            district = df1["Postal.District"].mode()
            m1 = m[m['Postal.District'] == int(district)]
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
            
            df1 = df1[["Date", "Address", "Avg area sqf", "Transacted Price", "Price (psf)", "Type.of.Sale"]]

            level = st.sidebar.slider('Level', 1, 70, 15)
            st.write('Level', level)

        else:
            st.write("System is not able to make any assessment for landed properties.")
            l1 = l[l['Project.Name'] == proj]
            district = l1["Postal.District"].mode()
            age_at_sale = datetime.date.today().year - l1["Completion Year"].max()
            Dist_Sch_Label = l1["Dist_Sch_Label"].mode()
            sch = l1["Nearest Sch"].mode()
            Distance_MRTexit = l1["Distance_Stn"].mode()
            stn = l1["Nearest Stn"].mode()
            TenureType_Ind = l1["TenureType_Ind"].mode()
            maxlevel = 1
        
            st.write('District', district.values[0])
            st.write('age at sale', age_at_sale)
            st.write('Sch Label', Dist_Sch_Label.values[0], "(", sch.values[0], ")")
            st.write('Distance from MRT (km)', Distance_MRTexit.values[0], "(", stn.values[0], ")")
            st.write('Tenure Type', TenureType_Ind.values[0])

            
            l1 = l1[["Date", "Address", "Avg area sqf", "Transacted Price", "Price (psf)", "Type.of.Sale"]]
        
        
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
        try:
            est_price = price(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                      level, maxlevel, district) * area
            est_price = int(est_price)
            est_price = '{:,.2f}'.format(est_price)
            st.success('**System assessment says:** Price is estimated to be: ${}'.format(est_price))
            assessment = prediction(age_at_sale, Dist_Sch_Label, Distance_MRTexit, TenureType_Ind, 
                                    level, maxlevel, area, district)
            st.success('**System assessment says:** {}'.format(assessment))
        except:
            st.write('**System is unable to make an assessment.**')

    # if st.button("Reset"):
    # 	pyautogui.hotkey("ctrl","F5")

    # st.balloons()
    
    if choice == "By Project Name":
        if proj in nonlanded:
            df1["Date"] = df1["Date"].astype('datetime64[ns]')
            m1["month_year"] = m1["month_year"].astype('datetime64[ns]')
            df1 = df1.sort_values(by = ['Date'], ascending = False)
            df1p = df1
            df1p.rename(columns = {'Avg area sqf':'Area (sqf)'}, inplace = True)
            df1p['Area (sqf)'] = (df1p.apply(lambda x: "{:,}".format(x['Area (sqf)']), axis=1))
            df1p['Transacted Price'] = (df1p.apply(lambda x: "{:,}".format(x['Transacted Price']), axis=1))
            df1p
            
            df1['Date'] = df1['Date'].map(lambda x : x.replace(day=1))
            df1a = df1.groupby(['Date'])['Price (psf)'].median().to_frame().reset_index()
            temp = proj + " Median Price"
            df1a.rename(columns = {'Price (psf)': temp}, inplace = True)
            df1a = pd.merge(df1a, m1,  how='left', left_on=['Date'], right_on = ['month_year'])
            df1a.rename(columns = {'Median Price':'District Resale Median Price'}, inplace = True)
            df1a = df1a[["Date", "District Resale Median Price", temp]]
            
            chart = alt.Chart(df1a)
            points = chart.transform_fold(
                fold=["District Resale Median Price"],
                as_=["Legend", "value"]
            ).encode(
                x=alt.X("Date:T", axis = alt.Axis(title = 'Date'.upper(), format = ("%b %Y"))),
                y=alt.Y("District Resale Median Price:Q", axis = alt.Axis(title = 'Price (psf)'.upper())),
                color=alt.Color("Legend:N", legend=alt.Legend(
                    orient='none',
                    legendX=80, legendY=-15,
                    direction='horizontal',
                    titleAnchor='middle')) 
            ).mark_line().interactive()
            
            line = chart.transform_fold(
                fold=[temp],
                as_=["Legend", "value"]
            ).encode(
                x=alt.X("Date:T", axis = alt.Axis(title = 'Date'.upper(), format = ("%b %Y"))),
                y=alt.Y(temp + ":Q", axis = alt.Axis(title = ''.upper())),
                color=alt.Color("Legend:N", legend=alt.Legend(
                    orient='none',
                    legendX=80, legendY=-15,
                    direction='horizontal',
                    titleAnchor='middle')) 
            ).mark_line().interactive()
                
            combine = alt.layer(points, line).interactive()

            st.altair_chart(combine.interactive(), use_container_width=True)
            
            st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.
            
        else:
            l1["Date"] = l1["Date"].astype('datetime64[ns]')
            l1 = l1.sort_values(by = ['Date'], ascending = False)
            lp = l1
            lp.rename(columns = {'Avg area sqf':'Area (sqf)'}, inplace = True)
            lp['Area (sqf)'] = (lp.apply(lambda x: "{:,}".format(x['Area (sqf)']), axis=1))
            lp['Transacted Price'] = (lp.apply(lambda x: "{:,}".format(x['Transacted Price']), axis=1))
            lp
            l1 = l1[["Date", "Price (psf)"]]
            temp = proj + " Median Price"
            l1.rename(columns = {'Price (psf)': temp}, inplace = True)

            chart2 = alt.Chart(l1)
            
            line2 = chart2.transform_fold(
                fold=[temp],
                as_=["Legend", "value"]
            ).encode(
                x=alt.X("Date:T", axis = alt.Axis(title = 'Date'.upper(), format = ("%b %Y"))),
                y=alt.Y(temp + ":Q"),
                color=alt.Color("Legend:N", legend=alt.Legend(
                    orient='none',
                    legendX=80, legendY=-15,
                    direction='horizontal',
                    titleAnchor='middle')) 
            ).mark_line().interactive()

            st.altair_chart(line2.interactive(), use_container_width=True)
            st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.
    else:
        st.success("App is working!!") # other tags include st.error, st.warning, st.help etc.
        
if __name__ == '__main__':
	main()
