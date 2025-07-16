import streamlit as st
import pandas as pd


mvlDict={'result_value_qualifier': ["SSI","ADL",'BDL','FD','LD','EFAI','FEF','FEQ','FFB','FFD',
            'FFS','H','ISP', 'ITNA','ITNM','JCW', 'NaN','NC','ND','NR', 'NS',
            'OC', 'P', 'prob_good', 'Interpolated', 'Q','Standardized to 25C']}

def choose_RVQs_Widgets(cleaned_df_list):

    # Allow users to choose starting RVQs and exceptions
    #********************************************************************************************************************************   
    st.markdown('#### 🌡️ Add RVQs')
    st.markdown('This step adds Result Value Qualifiers to cells in your files where the data might be atypical, erroneous, or missing.')

    def click_Begin_button():
        st.session_state.begin6 = True
    st.button("Let's Go!", type="primary", key='Begin_Button6', on_click=click_Begin_button)

    if st.session_state.begin6:
        st.markdown('##### ')
        st.markdown('##### Choose starting variable')
        st.markdown('From the first dropdown list, choose the starting variable for adding RVQs. RVQs will be added to each variable after, starting with the selected variable. ')
        st.markdown('If there are any varibales **after** this starting variable that should **not** have an RVQ, select these variables in the **Exceptions** list.')

        headers_list=list(cleaned_df_list[0].columns) #Updated cols

        #Setting States
        # If the button is clicked, the session state is set to true (button is clicked)
        def click_button():
            st.session_state.next6 = True

        # If selections are changed, the session state is set to False (button is unclicked, so user has to click again)
        def change_vars():
            st.session_state.next6 = False
            st.session_state.next7 = False
            st.session_state.allDone=False


        col1,col2, col3=st.columns(3)
        starting_rvq_var = col1.selectbox(label='Starting Variable',options=list(headers_list),index=None, on_change=change_vars, key='rvqVar')#select widget
        exceptions = col2.multiselect(label='Exception',options=list(headers_list), on_change=change_vars, key='rvqEx')#select widget. Exceptions are variables that wont have RVQs added

        #Next button
        st.button("Next", type="primary", key='Next_Button6', on_click=click_button)

        if st.session_state.next6==True:# If button is clicked
            return starting_rvq_var, exceptions

#-------------------------------------------------------------------------------------------------------
def match_rvq_to_user_codes_widgets():
    rvq_values=mvlDict['result_value_qualifier'] #Get the rvq values from dictionary

    st.markdown('######')
    st.write('##### Match any Data codes to RVQ codes.')
    st.html('See the <a href="https://docs.google.com/spreadsheets/d/e/2PACX-1vSckbimCcTEfNbIPlRAglNKadV4elz8AICViwNusOd_oKFEbjaelslDfehjo7A1IUHn3cukt7DeVCsS/pubhtml?gid=518408190&single=true" target="_blank">Master Validation List for a list of RVQs and thier meanings.</a> ')
    st.html("""
            <style>
            div.s {    
                font-size: 16px;
                }
            </style>

            <div class="s">
            For example, a <b>9999</b> Data code may represent the RVQ code  <b>ND</b> (Not Detected).<br>
            <b>Note:</b> To associate <b>empty data cells</b> with a certain RVQ, use <b>nan</b> as the Data Code. <br><br>

            <b>Detection Limits</b>
            <ul>
            <li>To capture detection limits, enter the starting letter (or character) before the actual limits.</li>
            <li>E.g. L0.4 represents a case where the detection limit is 0.4 (0.4 Below Detection Limit). In this case eneter <b>L</b> as the Data Code, and <b>BDL</b> as the RVQ code.</li>
            </ul>

            </div>                      
                """)

    usercodes=list()  #create a list for gettign the StringVar() entry from user 
    rvqcodes=list()   #create a list for gettign the StringVar() selection from user 

    #Setting States
    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.next7 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.next7 = False

    col1,col2, col3=st.columns(3)
    count=0
    for c in range(0,5): 
        count=count+1

        if count==1:
            data_code_label='Data Code'
            rvq_code_label= 'RVQ'
            lab_vis='visible'
        else:
            data_code_label=''
            rvq_code_label=''
            lab_vis='collapsed'

        # Text Widget for getting the data code
        code=col1.text_input(label=data_code_label, value=None, placeholder='9999',key=f'text{c}',on_change=change_vars,label_visibility=lab_vis)    
        usercodes.append(code)  #Add each entry to the list

        #Dropdown widget for RVQs
        RVQ=col2.selectbox(label=rvq_code_label,options=list(rvq_values),index=None, placeholder='ND',key=f'select{3+c}', on_change=change_vars,label_visibility=lab_vis)
        rvqcodes.append(RVQ)  #Add each selection to the list

    #Next button
    st.button("Next", type="primary", key='Next_Button3', on_click=click_button)

    if st.session_state.next7==True:

        #Remove NUll values
        usercodes=[uc for uc in usercodes if uc is not None]
        rvqcodes=[rvqc for rvqc in rvqcodes if rvqc is not None ]

        return usercodes,rvqcodes

#-------------------------------------------------------------------------------------------------------
def create_rvq_dictionary_from_user_input(supplementary_df_list,usercodes,rvqcodes):
    rvqdict={} #create an empty rvq dict

    #create a rvq dictionary
    for c in range(0,len(usercodes)): 
        userCode=usercodes[c] # Get the actual entry value stored in each 'code' in the list
        rvqCode=rvqcodes[c]   # Get the rvq code value stored in each 'code' in the list
        rvqdict[userCode]=rvqCode  # Create a final dictionary of usercode:rvq_from_MVL
    
    #Remove empty values in dictionary
    rvqdict = {i:j for i,j in rvqdict.items() if j != None}
    
    #save dict to dataframe and save as CSV
    rvqdf= pd.DataFrame(rvqdict.items(), columns=['Data code', "CanWIN's Result Value Qualifier"])
    rvqdf.to_csv('DataCodes_RVQ_curated.csv', index=False)

    #Add to the supplementary df list
    supplementary_df_list.append(rvqdf)

    return supplementary_df_list

#-------------------------------------------------------------------------------------------------------
def save_rvq_dict_tocsv(rvqdict):   
    # save dict to dataframe and save as csv
    rvqdf=pd.DataFrame(rvqdict.items(), columns=['Data code', "CanWIN's Result Value Qualifier"])
    rvqdf.to_csv('DataCodes_RVQ_curated.csv', index=False)


def add_RVQs_to_files(cleaned_df_list, starting_rvq_var, exceptions, usercodes,rvqcodes):

    temp_workin_list=[]
    for df in cleaned_df_list: 

        vars_with_rvqs=create_list_with_potential_rvq_variables(df, starting_rvq_var, exceptions)

        #Let us loop through this varibale list and check for actual instances of user codes and get the rows
        rvq_dict_per_Variable_List = [] #This will contain a list of dictionaries for each variable that has user codes in their column. E.g,  {variable: Temp; usercodes:L0.5, L8; Rows: 0,3}
        for variable in vars_with_rvqs:
            rvq_dict_per_Variable_List, df=checkFor_UserCodes_in_RVQVariable_Columns(df,usercodes,rvqcodes, variable, rvq_dict_per_Variable_List)
        
        #Let us create the RVQ column only for those Variables that actually have usercodes:
        df=create_RVQ_columns_for_Variables(rvq_dict_per_Variable_List,df)
            #final_df_list=save_and_download.save_final_dataframe(df_merged, csv, total_dfs, count, final_df_list) #Create csv file for data frame without dl still present in file
        temp_workin_list.append(df) #update the list for this processing

    cleaned_df_list=temp_workin_list
    return cleaned_df_list

#-------------------------------------------------------------------------------------------------------
def create_list_with_potential_rvq_variables(df, starting_rvq_var, exceptions):

    #Get all the columns
    all_columns=list(df.columns)

    #Find the index of the starting variable
    starting_rvq_var_index=all_columns.index(starting_rvq_var)

    # Slice the list
    vars_with_rvqs=all_columns[starting_rvq_var_index:]

    #Remove known Exceptions. Convert to a set for efficient lookup
    exceptions_set=set(exceptions) 

    # Update list excluding elements in exceptions_set
    vars_with_rvqs=[item for item in vars_with_rvqs if item not in exceptions_set]

    return vars_with_rvqs

#-------------------------------------------------------------------------------------------------------
def checkFor_UserCodes_in_RVQVariable_Columns(df,usercodes, rvqcodes, variable, rvq_dict_per_Variable_List):
    #Lets create a list of the rows and usercodes for each variable
    usercode_rows_per_variable_list=[]
    usercodes_per_variable_list=[]
    rvqcodes_per_variable_list=[]
    full_UserCode_per_variable_list=[] #Even though the entered user code is L, for ex, the full value in the cell may be L0.6 if it is a detection limit (ADL/BDL RVQ code)
    rvq_dict_per_Variable={}

    for usercode, rvqcode in zip(usercodes, rvqcodes):
        # Check for the presence of the usercode in each cell
        mask = df[variable].astype(str).str.contains(usercode,na=False) #.str.contains(...) returns a boolean Series indicating which rows contain your search string.

        # Check if there are any matches
        if mask.any():
            rows_with_userCodes=df[mask] #This filters the entire dataframe to include only the rows where the particular variable has a usercode
            
            for idx, value in rows_with_userCodes[variable].items(): #This gets the index (row) and value of the cells where the variable has a usercode value
                #st.write(f"User code {value} was found in column '{variable}' at row {idx}")

                #Append to the usercode and rows list for each variable (one varibale could have multiple occurances of the usercode in different rows)
                usercode_rows_per_variable_list.append(idx)
                usercodes_per_variable_list.append(value)

                #Append the full value of the cell in the variable column
                full_value=df[variable].iat[idx]
                full_UserCode_per_variable_list.append(full_value)

                #Also append the associated rvq code for that user code
                rvqcodes_per_variable_list.append(rvqcode)

                #Remove the full code from the Variable column and just leave  a blank space
                df[variable].iat[idx]= ''


    #Add the details to a dictionary only if the variable has any usercodes in its columns
    if usercode_rows_per_variable_list !=[]:
        rvq_dict_per_Variable['Variable']= variable 
        rvq_dict_per_Variable['UserCodes']= usercodes_per_variable_list
        rvq_dict_per_Variable['FullValue']= full_UserCode_per_variable_list
        rvq_dict_per_Variable['RVQCodes']= rvqcodes_per_variable_list
        rvq_dict_per_Variable['Rows']= usercode_rows_per_variable_list

        #Add this dictionary for each variable to a list 
        rvq_dict_per_Variable_List.append(rvq_dict_per_Variable)

    return rvq_dict_per_Variable_List, df

#-------------------------------------------------------------------------------------------------------
def create_RVQ_columns_for_Variables(rvq_dict_per_Variable_List, df):

    for rvq_dict in rvq_dict_per_Variable_List: # Loop through each rvq variable and detials in the dicts saved in this list

        #Find the position of this variable column in df.
        col_position=df.columns.get_loc(rvq_dict["Variable"])

        #Create Var_rvq name
        var_rvq_name=str(rvq_dict["Variable"])+'_Result_Value_Qualifier'

        #Enter a new empty RVQ column after this position
        df.insert(col_position+1,var_rvq_name,'')

        #Insert the RVQ code in the RVQ column at the correct row (same row as the user code in variable column)
        row_values=rvq_dict["Rows"]
        rvq_values=rvq_dict["RVQCodes"]
        whole_values=rvq_dict["FullValue"]
        for row, rvq, wv in zip(row_values,rvq_values,whole_values):
            rvqCode_string=rvq+' '+'['+ wv +']' #combining the RVQ code and the whole value in brackets for e.g BDL [L0.6]
            df[var_rvq_name].iloc[row]=rvqCode_string

    return df


#-------------------------------------------------------------------------------------------------------
# def filter_actual_RVQ_variables(rvq_dict_per_Variable_List):

#     final_RVQ_Variable_list=[]
#     for rvq_dict in rvq_dict_per_Variable_List:
#         for key, value in rvq_dict.items():

#             if key=='Variable':
#                 final_RVQ_Variable_list.append(value) 
#     return final_RVQ_Variable_list
