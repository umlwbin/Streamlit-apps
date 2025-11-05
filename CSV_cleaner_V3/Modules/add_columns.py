import streamlit as st


def how_many_vars_widget(cols):

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### How many fields would you like to add?')

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():
        st.session_state.addColsNext1 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.addColsNext1 = False

    # WIDGET CREATION --------------------------------------------
    left2, right2 = st.columns(2)
    var_num=left2.number_input(label="Number of fields to add", value=1, on_change=change_vars, key='addnum')
    st.button("Next", type="primary", key='addColsNext1_WidgetKey', on_click=click_button) #next button

    # IF BUTTON IS CLICKED --------------------------------------------
    if st.session_state.addColsNext1==True: #If next button is clicked
        if var_num:
            task_inputs=fields_to_add_widgets(cols, var_num)
            return task_inputs
        else:
            left2.error('Please enter a number!', icon="🚨")


def fields_to_add_widgets(cols, var_num):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('')
    st.markdown('##### Steps')
    st.markdown('1. Enter the name of the column to add')
    st.markdown('2. Enter the value for that column. **ℹ️ Note: The value will be the same throughout the column**')
    st.markdown(f'3. Enter the column number where it should be added in your file (first column is 1, last column of this data is {len(list(cols))} )')
    st.info('If you change your mind, just leave fields empty and click next, or change the number above. 🙂', icon="ℹ️")

    # WIDGET CREATION ---------------------------------------------------------------       
    variable_name_list=[]
    variable_value_list=[]
    col_number_list=[]

    # Create widgets to enter col, value and col position
    col1,col2,col3=st.columns(3)
    for c in range(0, var_num):
        variable_name=col1.text_input(label='Column variable name',placeholder='E.g. project_name', value=None, key='var')
        variable_name_list.append(variable_name)
        
        variable_value=col2.text_input(label='Variable value', placeholder="E.g. BaySys", value=None, key='val')
        variable_value_list.append(variable_value)

        col_number=col3.number_input(label='Column number', value=(len(list(cols))+1)+c, key='colnum')
        col_number_list.append(col_number)
    
    # Widget for next button
    st.button("Next", type="primary", key='addColsNext2_WidgetKey') #next button

    # IF BUTTON IS CLICKED --------------------------------------------
    if st.session_state.get("addColsNext2_WidgetKey") == True: #If next button is clicked
        left, right = st.columns([0.8, 0.2])

        #If they entered a variable name but no value
        for var, val in zip(variable_name_list, variable_value_list):
            if (var!=None) and (val==None):
                left.markdown('')
                left.warning(f'You have not entered a value for **{var}**. **{var}** wil be removed.', icon='⚠️')

        #If they entered nothing
        if all([t==None for t in variable_name_list]) and all([val==None for t in variable_value_list]):
            left.markdown('')
            left.warning("You haven't entered any variables so we will just ignore it!")

        #Create input dictionary for task function
        task_inputs = {
                "variable_names": variable_name_list,
                "values": variable_value_list,
                "columns": col_number_list
            }

        return task_inputs


#PROCESSING TASKS************************************************************************
def add_cols(df, variable_names,values,columns): 
    # Add the additional variables to new dataframe
    try:
        if variable_names:
            for va, val, pos in zip(variable_names, values, columns):
                df.insert(pos-1, va, val)
    
    except ValueError as e:
        st.markdown('')
        st.error("You already have that column name!",icon="🚨",)
    return df
