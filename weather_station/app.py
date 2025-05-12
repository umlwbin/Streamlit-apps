import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime as dt

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

def main():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('Weather Station Viewer ⛈️')
    st.sidebar.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/MMF%20Weather%20Station/img/st-laurent_17060_oct2022.jpeg?ref_type=heads", width=280)
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">

        <br><b>The Manitoba Métis Federation Weather Keeper Program</b> <br>
        The Weather Keeper Program is a collaboration between the Manitoba Métis Federation (MMF) and the Centre for Earth Observation Science (CEOS) at the University of Manitoba, to support the collection of atmospheric data in the Manitoba Great Lakes region. 
        This program is a co-developed, and jointly managed, monitoring network that will provide information on how the Manitoba Great Lakes respond to land-use changes and variability in weather.
        This program also gives insight into the local and regional effects of climate change. <br>
        The St. Laurent weather station, shown above, is one of the citizen-managed stations that provides current weather conditions in the area.
        <br><br>
                    
        <a href="https://canwin-datahub.ad.umanitoba.ca/data/project/mmf-weather-keeper" target=”_blank”>Download project data from CanWIN. <br><br></a>

        <b>What This App Does</b> <br>

        View past and current St. Laurent weather station data and compare to Environment and Climate Change Canada stations close by.<br><br> 
        Data is pulled from <a href="https://canwinmap.ad.umanitoba.ca/dashboards/weather-stations/?feature=11&additionalStations=true" target=”_blank”>CanWIN's interactive map dashboard.<br><br></a>  

                  
    </div>
    '''
    )


    # Clear output data
    # main_path=os.path.abspath(os.curdir)
    # _, _, files = next(os.walk(main_path))
    # files=[f for f in files if 'example' in f]

    # for f in os.listdir(main_path):
    #     if 'cwout' in f:
    #         os.remove(os.path.join(main_path, f))


    #Create a session state for the 'grab data' function, so that it happend only once while using the app.
    if 'pulledData' not in st.session_state:
        st.session_state.pulledData = False

    if 'result' not in st.session_state:
        st.session_state.result= None

    # Button to trigger the function
    st.markdown('#### Get the Data 🌤️')
    if st.button("Grab all weather station data"):
        st.session_state.pulledData = True
        
    # Display the spinner and run the function only when needed
    if st.session_state.pulledData:
        with st.spinner("Grabbing the latest weather station files and doing some cleaning..."):
            st.session_state.result=grab_data()
            all_dfs=st.session_state.result
            stl_avgs=all_dfs[0]
            eccc_df=all_dfs[1]
            newdf=all_dfs[2]
            st.session_state.pulledData = False
            options(stl_avgs,eccc_df, newdf)

    else:
        if st.session_state.result!=None: #When first reading function result is None
            stl_avgs=st.session_state.result[0]
            eccc_df=st.session_state.result[1]
            newdf=st.session_state.result[2]
            options(stl_avgs,eccc_df, newdf)



def grab_data():
    
    #st.info('Grabbing the latest weather station files and doing some cleaning...This might take a few seconds...', icon="ℹ️",)

    stl_raw_cols=['Datetime', 'Air Pressure', 'Air Temperature', 'Battery Voltage', 'Photosynthetically Active Radiation', 'Rain', 'Relative Humidity', 'Wind From Direction', 'Wind Speed', 'Wind speed of gust']
    eccc_raw_cols=['Datetime', '3-hour pressure tendency amount', '3-hour pressure tendency characteristic', '5-minute cumulative precipitation gauge filtered weight for minutes 55 to 60', 'Air Temperature', 'Average 10 meter wind speed over past 1 hour', 'Average 10 meter wind speed over past 10 minutes', 'Average 10 meter wind speed over past 2 minutes', 'Average air temperature over past 1 hour', 'Average snow depth over past 5 minutes', 'Average wind direction at 10 meters over past 2 minutes', 'Average wind speed at precipitation gauge over past 10 minutes', 'Data Availability', 'Datalogger panel temperature', 'Dew Point Temperature', 'Maximum 10 meter wind speed over past 1 hour', 'Maximum 10 meter wind speed over past 10 minutes', 'Maximum Air Temperature over past 1 hour', 'Maximum Air Temperature over past 24 hours', 'Maximum Air Temperature over past 6 hours', 'Maximum Battery Voltage over past 1 hour', 'Maximum Relative Humidity over past 1 hour', 'Mean Sea Level Pressure', 'Minimum Air Temperature over past 1 hour', 'Minimum Air Temperature over past 24 hours', 'Minimum Air Temperature over past 6 hours', 'Minimum Battery Voltage Past 1 Hour', 'Minimum Relative Humidity over past 1 hour', 'Precipitation Amount over past 1 hour', 'Precipitation Amount since last synoptic hour', 'Precipitation amount over past 24 hours', 'Precipitation amount over past 3 hours', 'Precipitation amount over past 6 hours', 'Rainfall amount over past 1 hour', 'Relative Humidity', 'Station Pressure', 'Timestamp of maximum wind speed over past hour', 'Vector average 10 meter wind direction over past 1 hour', 'Vectoral average 10 meter wind direction over past 10 minutes', 'Wet-bulb Temperature', 'Wind direction associated with the maximum wind speed at 10 meters over past 1 hour', 'Wind direction associated with the maximum wind speed at 10 meters over past 10 minutes']
    rows_stl=88178
    rows_eccc=8978

    #if st.session_state.pulledData == False:

    #Grab the data files from server
    url="https://sta-canwin.ad.umanitoba.ca/loader/11"
    stl_df=pd.read_csv(url, skiprows = rows_stl+1, names=stl_raw_cols)
    
    url2="https://sta-canwin.ad.umanitoba.ca/loader/18"
    eccc_df=pd.read_csv(url2, skiprows= rows_eccc+1, names=eccc_raw_cols)

    #Set pulledData to true
    st.session_state.pulledData = True

    #-------------------------------------------------------------------------------------------------------
    
    #Lets do some data Cleaning
    # 1. Add RVQs
    
    cols=stl_df.columns
    for col in cols:
    
        if col=='Datetime':
            continue
        else:
            if col=='Rain':
                stl_df.rename(columns={'Rain':'Precipitation'}, inplace=True)
                col='Precipitation'
                
            RVQ_name=col+'_Result_Value_Qualifier'
            idx=stl_df.columns.get_loc(col)    #get index for column
            stl_df.insert(idx+1,RVQ_name, '')  #insert RVQ column
    
    
    # 2. Subsetting date and time into lists for filtering in next steps
    year=pd.DatetimeIndex(stl_df['Datetime']).year
    month=pd.DatetimeIndex(stl_df['Datetime']).month
    day=pd.DatetimeIndex(stl_df['Datetime']).day
    hour=pd.DatetimeIndex(stl_df['Datetime']).hour
    
    import numpy as np
    # 3. Finding bad data
    #.............................................................................................................
    air_pres_list=[]
    for index, row in stl_df.iterrows():
    
        col='Air Pressure'
        if row[col]> 1070 or row[col]< 660:
            stl_df.at[index,col]=None
    
        col='Photosynthetically Active Radiation'
        if row[col]> 2500 or row[col]< 0:
            stl_df.at[index,col]=None
    
        col='Air Temperature'
        if row[col]> 75 or row[col]< -40:
            stl_df.at[index,col]=None
                
        col='Relative Humidity'
        if row[col]> 100 or row[col]< 0:
            stl_df.at[index,col]=None 
        
        col='Precipitation'
        if row[col]> 127 or row[col]< 0:
            stl_df.at[index,col]=None
    
        col='Wind Speed'
        if row[col]> 115 or row[col]< 0:
            stl_df.at[index,col]=None
    
        col='Wind speed of gust'
        if row[col]> 115 or row[col]< 0:
            stl_df.at[index,col]=None
    
        #Labeling bad data for wind and gust speed that are both 40 m/s using standardized label prob\_bad
        if row['Wind Speed'] == row['Wind speed of gust'] and row['Wind Speed']>115:
            stl_df.at[index,'Wind Speed']=None
            stl_df.at[index,'Wind speed of gust']=None
    
        #Labeling bad data for wind directions that fall in dead zone of anemometer using standardized label prob\_bad
        if row['Wind From Direction'] > 355 and row['Wind From Direction'] <360:  
            stl_df.at[index,'Wind From Direction']=None
    
        #Labeling bad data for Precipitation measurements in December, January, and February using standardized label prob\_bad
        if(month[index] == 12 or  month[index] == 1 or month[index] == 2):
            stl_df.at[index,'Precipitation']=None
    
        #Labeling bad data for Precipitation measurements in transitional seasons when temperature is below 1 degree Celsius and precipitation measurements greater than 0 using standardized label prob\_bad
        if month[index] == 10 and row['Precipitation']>0 and row['Air Temperature']<=1:
            stl_df.at[index,'Precipitation']=None
    
        if month[index] == 11 and row['Precipitation']>0 and row['Air Temperature']<=2:
            stl_df.at[index,'Precipitation']=None
    
        if month[index] == 3 and row['Precipitation']>0 and row['Air Temperature']<=2:
            stl_df.at[index,'Precipitation']=None
    
        if month[index] == 4 and row['Precipitation']>0 and row['Air Temperature']<=2:
            stl_df.at[index,'Precipitation']=None
        
        #Labeling bad data for Precipitation measurements recorded on deployment date of weather station when testing was completed using standardized label prob\_bad
        if year[index]==2021 and month[index]==9 and day[index]==24 and row['Precipitation']>0:
            stl_df.at[index,'Precipitation']=None
    #.............................................................................................................
    
    #Create a date and hour column by splitting the datetime
    stl_df['date_and_hour'] = stl_df['Datetime'].str.split(':')
    stl_df['date_and_hour']=[d[0] for d in stl_df['date_and_hour'] ]
    
    #Group by this date and hour column and take the mean
    stl_avgs = stl_df.groupby(stl_df.date_and_hour, as_index=False).mean(numeric_only=True)
    
    #Add the unique date+hours as the datetime col in the averages df
    stl_avgs['Datetime']=pd.to_datetime(stl_df['date_and_hour'].unique())

    dates=stl_avgs.pop('Datetime')
    stl_avgs.insert(1,'Datetime',dates)
    
    #Update column names to have stl at end (except datetime)
    stl_cols=[]
    for c in stl_avgs.columns:
        if c=='Datetime':
            stl_cols.append(c)
        else:
            stl_cols.append(c+'_StL')

    stl_avgs.columns=stl_cols
        
    
    #Remove millisecs from ECC datetimes
    eccc_df[['Datetime','MS']] = eccc_df['Datetime'].str.split('.', expand=True)
    eccc_df.drop(['MS'], axis=1)

    #format='%Y-%m-%d %H:%M:%S'
    
    #Convert to datetime
    eccc_df['Datetime']=pd.to_datetime(eccc_df['Datetime'])


    #Drop variables
    eccc_df = eccc_df.drop(columns=['3-hour pressure tendency amount', '3-hour pressure tendency characteristic',
                                '5-minute cumulative precipitation gauge filtered weight for minutes 55 to 60',
                                'Average 10 meter wind speed over past 10 minutes', 'Average 10 meter wind speed over past 2 minutes', 'Average snow depth over past 5 minutes', 
                                'Average wind direction at 10 meters over past 2 minutes', 'Average wind speed at precipitation gauge over past 10 minutes', 
                                'Data Availability', 'Datalogger panel temperature', 'Dew Point Temperature', 'Maximum 10 meter wind speed over past 1 hour', 
                                'Maximum 10 meter wind speed over past 10 minutes', 'Maximum Air Temperature over past 1 hour','Maximum Air Temperature over past 24 hours', 
                                'Maximum Air Temperature over past 6 hours','Maximum Battery Voltage over past 1 hour','Maximum Relative Humidity over past 1 hour',
                                'Minimum Air Temperature over past 1 hour','Minimum Air Temperature over past 24 hours', 'Minimum Air Temperature over past 6 hours',
                                'Minimum Battery Voltage Past 1 Hour', 'Minimum Relative Humidity over past 1 hour', 'Precipitation Amount since last synoptic hour',
                                'Precipitation amount over past 24 hours', 'Precipitation amount over past 3 hours', 'Precipitation amount over past 6 hours',
                                'Timestamp of maximum wind speed over past hour','Vectoral average 10 meter wind direction over past 10 minutes', 'Wet-bulb Temperature',
                                'Wind direction associated with the maximum wind speed at 10 meters over past 1 hour', 'Wind direction associated with the maximum wind speed at 10 meters over past 10 minutes','MS'])
    
    #From St.L
    stl_avgs = stl_avgs.drop(columns=['Battery Voltage_StL','Photosynthetically Active Radiation_StL'])
    
    #merge dataframes into one
    out = (pd.merge(stl_avgs, eccc_df,how='outer', on='Datetime'))
    
    #Cropping for only the period of ECC data
    #get the first ECC date
    ecc_first_date=eccc_df['Datetime'][0]
    
    #crop the dataframe ot start at that date
    newdf=out[out.Datetime >=ecc_first_date].reset_index(drop=True)


    #Merge data frames with the last curated dfs (this will be an ongoing process so as to reduce cleaning time)
    eccc_df_curated=pd.read_csv('eccc_df_curated.csv')
    stl_df_curated=pd.read_csv('stl_avgs_curated.csv')
    newdf_curated=pd.read_csv('newdf_curated.csv')

    stl_df_curated['Datetime']=pd.to_datetime(stl_df_curated['Datetime'], format='%Y-%m-%d %H:%M:%S')
    eccc_df_curated['Datetime']=pd.to_datetime(eccc_df_curated['Datetime'], format='%Y-%m-%d %H:%M:%S')
    newdf_curated['Datetime']=pd.to_datetime(eccc_df_curated['Datetime'], format='%Y-%m-%d %H:%M:%S')

    stl_avgs=pd.concat([stl_df_curated, stl_avgs], axis=0, ignore_index=True)

    eccc_df=pd.concat([eccc_df_curated, eccc_df], axis=0)
    newdf=pd.concat([newdf_curated, newdf], axis=0)

    #options(stl_avgs,eccc_df, newdf)
    return [stl_avgs,eccc_df, newdf]


def options(stl_avgs,eccc_df, newdf):

    st.markdown('#####')
    st.markdown('#### What would you like to do? ✍🏼')

    #Radio Widget for choices
    choice=st.radio(
    "Select an option",
    ["Visualize St. Laurent data", "Plot both St. Laurent and ECCC station data"],
    index=None,)



    if choice=="Visualize St. Laurent data":
        select_var(stl_avgs,newdf)

    if choice=="Plot both St. Laurent and ECCC station data":
        compare(newdf) 
    

def select_var(stl_avgs,newdf):

    cols=list(stl_avgs.columns)
    cols=[c for c in cols if ('date' not in c) and ('Date' not in c) and ('Direction' not in c) and ('gust' not in c)]

    st.markdown('#####')
    st.markdown('#### Choose the variable you would like to plot')


    #CREATE WIDGETS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked1' not in st.session_state:
        st.session_state.clicked1 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked1 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked1 = False

    #Widgets
    left, right = st.columns(2)
    var=left.selectbox("Select variable and ckick **Plot**",options=cols, on_change=change_vars)
    left.button("Plot", type="primary", key='1', on_click=click_button)

    if st.session_state.clicked1:

        if var:
            # Call next function
            plot(stl_avgs,var)
        else:
            st.warning('Please choose a variable', icon="⚠️")


def plot(stl_avgs,var):


    #Lets get some max info
    max_var_info=stl_avgs.loc[stl_avgs[var].idxmax()]
    max_var=max_var_info[var]
    max_var_date=max_var_info['Datetime']
    max_var_date=max_var_date.strftime('%B %d, %Y')

    #Lets get some min var info
    min_var_info=stl_avgs.loc[stl_avgs[var].idxmin()]
    min_var=min_var_info[var]
    min_var_date=min_var_info['Datetime']
    min_var_date=min_var_date.strftime('%B %d, %Y')

    #Get the latest date information
    most_recent_date_info = stl_avgs.loc[stl_avgs['Datetime'].idxmax()]
    most_recent_date =most_recent_date_info['Datetime']
    most_recent_date_var =most_recent_date_info[var]


    #Minus a year
    from dateutil.relativedelta import relativedelta
    year_ago = most_recent_date - relativedelta(years=1)


    #Lets get some variable names and other info
    if 'temp' in var or 'Temp' in var:
        #For the Cards
        varname=var[:-4]
        unit='°C'
        col='red' #for plotting
        icon1='🔥'
        icon2='🥶'
        icon3='🌡️'

    elif 'Precipitation' in var:
        #For the Cards
        varname=var[:-4]
        unit='mm'
        col='green' #for plotting 
        icon1='⛈️'
        icon2='🌤️'
        icon3='🌧️'
        
    elif 'Pressure' in var:
        #For the Cards
        varname=var[:-4]
        unit='mb'
        col='mediumvioletred' #for plotting    
        icon1='👆🏼'
        icon2='👇🏼'
        icon3='🌎'  

    
    elif 'Humidity' in var:
        #For the Cards
        varname=var[:-4]
        unit='%'
        col='orange' #for plotting
        icon1='😰'
        icon2='🥵'
        icon3='💧'            

    elif 'Wind Speed' in var:
        #For the Cards
        varname=var[:-4]
        unit=' km/hr'
        col='royalblue' #for plotting  
        icon1='🍃🍃'
        icon2='🍃'
        icon3='💨'             
    


    #Lets create some cards ~~~~~~~~~~~~~~~~~~~~~~~~~~
    from streamlit_card import card

    left,right=st.columns(2)

    with left.container():

        #Highest and Lowest values
        card(
            title=f'{icon1} Max {varname}',
            text=f'The highest {varname} for the recording period was {round(max_var)} {unit} on {max_var_date}.',
            styles={
                "card": {
                    "width": "100%",
                    "height": "150px",
                    "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                    "margin":'20px 0px 0px 0px',
                    'border-radius': '20px',
                },

                "text": {
                "font-family": "inherit",
                "font-weight": "normal", 
                "color": "black",
                },

                "title":{
                    "font-weight": "normal",
                    "color": "black",
                    "font-size":20

                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, 0)"  # <- make the image not dimmed anymore
                }
            }
        )

    with right.container():
        card(
            title=f'{icon2} Min {varname}',
            text=f'The lowest {varname} for the recording period was {round(min_var)} {unit} on {min_var_date}.',
            styles={
                "card": {
                    "width": "100%",
                    "height": "150px",
                    "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                    "margin":'20px 0px 0px 0px',
                    'border-radius': '20px'
                    
                },

                "text": {
                "font-family": "inherit",
                "font-weight": "normal", 
                "color": "black",
                },

                "title":{
                    "font-weight": "normal",
                    "color": "black",
                    "font-size":20

                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, 0)"  # <- make the image not dimmed anymore
                }
            }
        )

    #Todays valaue and this time last year
    if pd.Timestamp(year_ago) in stl_avgs['Datetime'].tolist(): #Check if the date from a year before is in the file

        #Get the var value from last year
        year_ago_info=stl_avgs.loc[stl_avgs['Datetime'] == year_ago]
        year_ago_var=list(year_ago_info[var])[0]

        #Convert to String
        most_recent_date=most_recent_date.strftime('%B %d, %Y')
        year_ago=year_ago.strftime('%B %d, %Y')

    with left.container():

        #Highest and Lowest values
        card(
            title=f'{icon3} Today\'s {varname}',
            text=f'The {varname} for today, {most_recent_date} is {round(most_recent_date_var)} {unit}.',
            styles={
                "card": {
                    "width": "100%",
                    "height": "150px",
                    "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                    "margin":'20px 0px 0px 0px',
                    'border-radius': '20px'
                },

                "text": {
                "font-family": "inherit",
                "font-weight": "normal", 
                "color": "black",
                },

                "title":{
                    "font-weight": "normal",
                    "color": "black",
                    "font-size":20

                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, 0)"  # <- make the image not dimmed anymore
                }
            }
        )

    with right.container():
        card(
            title=f'{icon3} {varname} this time last year',
            text=f'The {varname} for this time last year, {year_ago} was {round(year_ago_var)} {unit}.',
            styles={
                "card": {
                    "width": "100%",
                    "height": "150px",
                    "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                    "margin":'20px 0px 0px 0px',
                    'border-radius': '20px'
                    
                },

                "text": {
                "font-family": "inherit",
                "font-weight": "normal", 
                "color": "black",
                },

                "title":{
                    "font-weight": "normal",
                    "color": "black",
                    "font-size":20

                },
                "filter": {
                    "background-color": "rgba(0, 0, 0, 0)"  # <- make the image not dimmed anymore
                }
            }
        )

    # AVERAGE PLOT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    fig = px.scatter(stl_avgs, x='Datetime', y=var)
    fig.update_layout(title_text=f"Average 1 hour {var[:-4]} at St. Laurent", xaxis_title='DateTime', yaxis_title=var[:-4], height=500,
                        yaxis = dict(tickfont =dict(size=14)),xaxis = dict(tickfont =dict(size=14)),font=dict(size=14), plot_bgcolor='ghostwhite', legend= {'itemsizing': 'constant'})
    fig.update_traces(marker={'size': 3, 'color':col})
    fig.update_xaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')
    fig.update_yaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')
    
    st.plotly_chart(fig)


def compare(newdf):

    
    cols=['Air Temperature', 'Relative Humidity', 'Air Pressure']
    st.markdown('#####')
    st.markdown('#### Choose the variable you would like to compare between the two stations')


    #CREATE WIDGETS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked2' not in st.session_state:
        st.session_state.clicked2 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked2 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked2 = False

    #Widgets
    left, right = st.columns(2)
    var=left.selectbox("Select variable and ckick **Plot**",options=cols, on_change=change_vars)
    left.button("Plot", type="primary", key='2', on_click=click_button)


    if st.session_state.clicked1:

        if var:
            # Call next function
            compare_plot(newdf,var)
        else:
            st.error('Please choose a variable', icon="❗️")
    

def compare_plot(newdf,var):
    import numpy as np

    # AVERAGE COMPARISON
    # Var names
    short_names=['Temp', 'Pres', 'RH']
    stl_var_names= ['Air Temperature_StL','Air Pressure_StL', 'Relative Humidity_StL']
    ECC_var_names=['Air Temperature','Station Pressure', 'Relative Humidity']
    colors=[px.colors.qualitative.Plotly, px.colors.qualitative.Alphabet, px.colors.qualitative.D3]
    units=['(°C)', '(mb)', '(%)'] 

    c=-1
    for v_name in stl_var_names:
        c=c+1
        if var in v_name:

            newdf[v_name]=newdf[v_name].round(3) #round the values
            
            if v_name=='Air Pressure_StL':
                newdf['Station Pressure'] = newdf['Station Pressure'].replace(0, np.nan)
                
            fig = px.scatter(newdf, x='Datetime', y=[stl_var_names[c], ECC_var_names[c]], color_discrete_sequence=colors[c])
            fig.update_layout(title_text=f"Average 1 hour {ECC_var_names[c]} at St. Laurent, Manitoba vs ECCC weather station at Oakpoint, Manitoba", xaxis_title='DateTime', 
                                yaxis_title=f'{ECC_var_names[c]} {units[c]}', legend_title=ECC_var_names[c], legend= {'itemsizing': 'constant'}, height=550,plot_bgcolor='ghostwhite',
                                yaxis = dict(tickfont =dict(size=14)),xaxis = dict(tickfont =dict(size=14)),font=dict(size=14), hovermode="x unified")
            
            fig.update_traces(hovertemplate=None, marker={'size': 3})
            fig.update_xaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')
            fig.update_yaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')

            series_names = ['St.L_'+short_names[c], 'ECCC_'+short_names[c]]
            for idx, name in enumerate(series_names):
                fig.data[idx].name = name

            st.plotly_chart(fig)

main()