import streamlit as st
import pandas as pd
import requests


#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

# GEt CanWIN Logo
logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
st.sidebar.image(logo, width=250)

# Title and Description
st.sidebar.title('CanWIN Standardized Vocabulary 📖')
st.sidebar.html("""
                <style>
                div.s {    
                    font-size: 20px;
                    h1{font-size: 22px;}
                    ul,ol {font-size: 20px; color: #333333; margin-bottom: 24px;}
                    }
                </style>

                <div class="s">
                    Find standardized names for common arctic/marine/freshwater variables
                    <br><br>
                    <h1>Steps</h1>
                    <ol>
                    <li>Find your varibale Category from the dropdown list</li>
                    <li>Look at each standardized varibale name under that category, and find the defnition that best fits your variable</li>
                    <li>Add the <b>Source Link</b> for the standardized term to your data dictionary</li>
                <li>All done!! 🥳</li>
                    </ol>                
                </div>
                    """)


# Constants for Google Sheets
SHEET_ID = '1jodEHgJm6uEpanvpnUqVAFutbWBgGfrISwAyDaaGHI0'
SHEET_NAME = 'Sheet1'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{{SHEET_ID}}/gviz/tq?tqx=out:csv&sheet={{SHEET_NAME}}'

r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={SHEET_ID}&output=csv')
open('dataset.csv', 'wb').write(r.content)

# Read the Google Sheet into a DataFrame
df = pd.read_csv('dataset.csv', header=0)

#Get the common variable names
common_names=[c for c in df['Common Variable Name'] if str(c)!='nan']

c=0
var_dict={}
start=False

df_length=len(df.index) #length of dataframe
for cn in common_names:

    #First line of category
    df_cn=df['Common Variable Name'].iloc[c]
    if df_cn==cn:
        start=True

        stNames_list=[] #list for each standardized name in category
        canwin_stNames_list=[] #list for each canwin standardized name in category
        descrip_list=[] #list for each description in category
        link_list=[] #list for each BODC link in category
        vocab_list=[] #source vocabulary

        #loop through the standardized names and descriptions under each category 
        while start==True and c<df_length-1:
            c=c+1 #keep counting for each row

            # If we encounter a blank line (this means there is a new category) then set start to False and break loop
            if str(df['Source Standardized Name'].iloc[c])=='nan': 
                start=False
                continue

            # If not, add st names, descriptions,links,vocab names
            stNames_list.append(df['Source Standardized Name'].iloc[c])
            canwin_stNames_list.append(df['CanWIN Standardized Name'].iloc[c])
            descrip_list.append(df['Description'].iloc[c])
            link_list.append(df['Link'].iloc[c])
            vocab_list.append(df['Source'].iloc[c])

        # Create a dictionary for each category, standardized names and descriptions
        var_dict[cn]=[stNames_list,canwin_stNames_list, descrip_list,link_list,vocab_list]



# Font size for Select Box Labes
tabs_font_css = """
<style>
div[class*="stSelectbox"] label p {
  font-size: 18px;
}
</style>
"""
st.write(tabs_font_css, unsafe_allow_html=True)

# Create dropdown menu for common variables
var_selection = st.selectbox(label='Choose the variable category', options=common_names, placeholder='Alkalinity')

for k,v in var_dict.items():
    if var_selection==k:
        #Get the potential standardized varibale names
        stand_names=list(v[0])
        canw_stand_names=list(v[1])
        descriptions=list(v[2])
        bodc_links=list(v[3])
        vocabs=list(v[4])


        # add select widget
        stan_selection = st.selectbox(options=canw_stand_names, label=f'Standardized variable names under **{var_selection}**')

        st.divider()  # 👈 Draws a horizontal rule

        for sn,csn, d, bl,v in zip(stand_names,canw_stand_names,descriptions,bodc_links,vocabs):
            c=c+1

            if stan_selection==csn: #if the standardized name selected is = to the standardized name in the loop currently

                #Give definition
                st.markdown(' ')
                st.markdown(f'<span style="font-size: 20px;">**Definition for {csn}**</span>', unsafe_allow_html=True)
                st.markdown(f'<span style="font-size: 18px;">{d}</span>', unsafe_allow_html=True)
                #st.markdown(f'')

                #Give the BODC/CF link
                if v=='BODC':
                    v_long='British Oceanographic Data Centre (BODC) vocabulary'
                else:
                    v_long='Climate and Forecast (CF) vocabulary'
                
                st.markdown(' ')
                st.markdown(f'<span style="font-size: 20px;">**Source vocabulary for this term**</span>', unsafe_allow_html=True)
                st.markdown(f'<span style="font-size: 18px;">{v_long}</span>', unsafe_allow_html=True)
                st.markdown(' ')
                st.markdown(f'<span style="font-size: 20px;">**{v} preferred label**</span>', unsafe_allow_html=True)
                st.markdown(f'<span style="font-size: 18px;">{sn}</span>', unsafe_allow_html=True)
                st.markdown(' ')
                st.markdown(f'<span style="font-size: 20px;">**Source link**</span>', unsafe_allow_html=True)
                st.markdown(f'<span style="font-size: 18px;">{bl}</span>', unsafe_allow_html=True)
            