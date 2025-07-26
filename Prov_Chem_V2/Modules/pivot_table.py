import streamlit as st
import pandas as pd
import copy

def restructure_widgets(cleaned_df_list):
    st.markdown('-------')
    st.markdown('##### 🗒️ Pivoting your Data Table')
    st.markdown('This step cleans a provincial file that contains a column with the variables/parameters and a column with values.')

    if 'pivotBegin' not in st.session_state:
        st.session_state.pivotBegin = False

    def click_Begin_button():
        st.session_state.pivotBegin = True
        st.session_state.PivotNext1 = False
        st.session_state.PivotNext2 = False

        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin= st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone = False  

    st.button("Let's Go!", type="primary", key='Begin_Button2', on_click=click_Begin_button)

    if st.session_state.pivotBegin: #Lets go button is pressed

        #Check for the VARIABLE and VALUE columns
        st.markdown('#####')
        st.markdown('##### Choose the Variable and the Value columns')

        cols=list(cleaned_df_list[0].columns)

        #Potential variable and value columns
        ind0=None
        ind1=None
        for index, item in enumerate(cols):
            string1='VARIABLE_NAME'
            string2='Parameter'
            string3='VALUE'
            string4='Result'

            if  string1.lower() in item.lower() or string2.lower() in item.lower():
                ind0 = index
            if string3.lower() in item.lower() or string4.lower() in item.lower():
                ind1= index
     
        #Setting States
        # If the button is clicked, the session state is set to true (button is clicked)
        def click_button():
            st.session_state.PivotNext1 = True

        # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
        def change_vars():
            st.session_state.PivotNext1 = False
            st.session_state.allDone=False

        col1,col2, col3=st.columns(3, vertical_alignment='bottom')
        var_col = col1.selectbox(label='Select the Variable column',options=cols, key='selVarCol', on_change=change_vars, index=ind0)
        value_col = col2.selectbox(label='Select the Value column',options=cols,key='selValCol', on_change=change_vars, index=ind1)
        
        #Next button
        col3.button("Next", type="primary", key='Next_Button02', on_click=click_button)

        if st.session_state.PivotNext1==True: #Next button is pressed

            if (var_col==None and value_col==None) or (var_col!=None and value_col==None) or (var_col==None and value_col!=None):
                st.error('No Variable or Value column was selected. Please try again.', icon="🚨")
            else:      
                additional_params=combine_values_with_headers_radio_widget(cols)
                return var_col,value_col, additional_params

def combine_values_with_headers_radio_widget(cols):

    #Are there other columns to add to the variable name?
    st.markdown('#####')
    st.markdown('##### Combine values from other columns to the variable names (column headers)')
    st.markdown('You could add the **Units**, **VMV codes** or **Varibale codes** from corresponding columns (e.g, Temperature_degC_567). ')

    def change_radio():
        st.session_state.pivotRadio1 = True
        st.session_state.begin3 = False #The clean headers lets go button is deactivated
        st.session_state.begin4 = False #iso date lets go button is deactivated
        st.session_state.begin5 = False #parse date lets go button is deactivated
        st.session_state.begin6 = False #rvq lets go button is deactivated
        st.session_state.PivotNext2 = False # So they have to press the next button again

    add_params_radio=st.radio("Would you like to add a column value to the variable header names, e.g, units?", ["Sure! 🤩", "Nah, I'm good 🙃"], on_change=change_radio,args=() , index=None)

    if add_params_radio=="Sure! 🤩": # Sure, add the additional parameters to the variable column name
        additional_params=combine_values_with_headers_widgets(cols)
        return additional_params

    if add_params_radio=="Nah, I'm good 🙃":
        st.session_state.PivotNext2 = True # It's like they pressed the next button. This has to be true for the next filter function to run.
        return None

def combine_values_with_headers_widgets(cols):
        st.markdown('######')
        st.markdown('###### Great! Choose the column(s) with the value you would like to add to the variable header names. These columns will then be removed.')
        #Setting States
        # If the button is clicked, the session state is set to true (button is clicked)
        def click_button():
            st.session_state.PivotNext2 = True

        # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
        def change_vars():
            st.session_state.PivotNext2 = False

        #Find potential unit, vmv, and variable codes (typical to add to the column headers)
        pot_units='UNIT'
        pot_vmv_codes='VMV'
        pot_var_codes='VARIABLE_CODE'

        units, vmv_codes, var_codes= None, None, None

        for col in cols:
            if pot_units.lower() in col.lower():
                units=col
            if pot_vmv_codes.lower() in col.lower():
                vmv_codes=col
            if pot_var_codes.lower() in col.lower():
                var_codes=col

        #Check if any of the default have been found
        if all(v is None for v in [units, vmv_codes, var_codes]):
            default_value=None
        else:
            default_value=[v for v in [units, vmv_codes, var_codes] if v!=None ]

        col1,col2, col3=st.columns(3, vertical_alignment='bottom')

        additional_params=col1.multiselect("Select one or more columns",cols, default=default_value, on_change= change_vars)
        col2.button("Next", type="primary", key='Next_Button3', on_click=click_button)

        if st.session_state.PivotNext2:
            return additional_params

def filter_df_for_each_variable(var_col,value_col, additional_params):

    # Create a deep copy of the current list in session state. We will work on this copy
    cleaned_df_list=copy.deepcopy(st.session_state.cleaned_df_list)

    # Push current version to history before makign any changes
    st.session_state.df_history.append(copy.deepcopy(st.session_state.cleaned_df_list))

    # Clear redo stack since we are making a new change
    st.session_state.redo_stack.clear()

    for i, df in enumerate(cleaned_df_list):
        filtered_dfs=[]

        unique_variables=df[var_col].unique() #Extract variable strings and find unique ones
        unique_variables = [item for item in unique_variables if item==item] #nan!=nan, removes nans 

        for var in unique_variables:
            filtered_df = df[df[var_col] == var]#filter the dataframe for only the rows where the variable is var
            filtered_df = filtered_df.rename(columns={value_col: var}) #Change the name 'VALUE' to the variable name (df is now filtered to one variable)
            filtered_df=filtered_df.drop(var_col, axis=1) #remove 'the Varibale_Name column'

            #Move variable column to end
            extracted_column = filtered_df[var]# Extract the variable column
            filtered_df = filtered_df.drop(columns=[var])#Drop the column from its original position
            filtered_df[var]=extracted_column

            filtered_df=filtered_df.reset_index(drop=True) #reset the index
            #call add variable code and vmv code fuction
            filtered_dfs=add_vmv_and_variable_code(var, filtered_df, filtered_dfs, additional_params)
        
        # Concatenate filtered variable dataframes
        df_merged=merge_filtered_dfs(filtered_dfs)

        #Reset Index
        df_merged.reset_index(drop=True, inplace=True)

    # Assign merged_df back to the same position in the list
    cleaned_df_list[i] = df_merged

    #Update the cleaned list in session state
    st.session_state.cleaned_df_list=cleaned_df_list

def add_vmv_and_variable_code(var, filtered_df, filtered_dfs, additional_params):

    if additional_params==None:
        #Dont add any additional parameters to the variable name, just add the filtered df to list and return
        filtered_dfs.append(filtered_df) #append the filtered data frame to data frame list
        return filtered_dfs
    else:
        if not filtered_df.empty:

            # Get the values from the first row of the additional parameters columns
            first_row_values = list(filtered_df.loc[0, additional_params])

            # Combine them with underscores
            combined_str = "_".join(str(x) for x in first_row_values)

            filtered_df.rename(columns={var: f"{var}_{combined_str}"}, inplace=True)# Rename the variable column to include the additional parameters, for e.g temp_C_78595
            filtered_df=filtered_df.drop(additional_params, axis=1) #remove the parameters columns
            filtered_dfs.append(filtered_df) #append the filtered data frame to data frame list
            return filtered_dfs

def merge_filtered_dfs(filtered_dfs):
    # MERGE all the filtered dataframes together
    df_merged=pd.concat(filtered_dfs, ignore_index=True) #merge all variables into one dataframe
    return df_merged
