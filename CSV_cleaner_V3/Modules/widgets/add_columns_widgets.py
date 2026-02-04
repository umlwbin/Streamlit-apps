import streamlit as st

# ---------------------------------------------------------
# STEP 1 — Choose number of fields
# ---------------------------------------------------------
def how_many_vars_widget(df):
    cols = df.columns

    st.markdown("##### How many fields would you like to add?")

    # Reset Step 2 if number changes
    def reset_step():
        st.session_state.addColsStep2_active = False

    var_num = st.number_input(
        "Number of fields to add",
        min_value=1,
        value=1,
        on_change=reset_step,
        key="addcols_num"
    )

    # Step 1 button — activates Step 2
    if st.button("Next", key="addcols_step1"):
        st.session_state.addColsStep2_active = True

    # If Step 2 is not active, stop here
    if not st.session_state.get("addColsStep2_active", False):
        return None

    # Otherwise show Step 2
    return fields_to_add_widgets(cols, var_num)


# ---------------------------------------------------------
# STEP 2 — Enter column details
# ---------------------------------------------------------
def fields_to_add_widgets(cols, var_num):

    st.markdown("##### Steps")
    st.markdown("1. Enter the name of the column to add")
    st.markdown("2. Enter the value for that column")
    st.markdown(f"3. Enter the column number (1 to {len(cols)+1})")
    st.info(
        "If you change your mind, leave fields empty and click Next, "
        "or change the number above.",
        icon="ℹ️"
    )

    variable_names = []
    variable_values = []
    column_numbers = []

    col1, col2, col3 = st.columns(3)

    for i in range(var_num):
        name = col1.text_input(
            "Column name",
            key=f"addcol_name_{i}",
            placeholder="e.g., project_name"
        )
        value = col2.text_input(
            "Value",
            key=f"addcol_value_{i}",
            placeholder="e.g., BaySys"
        )
        colnum = col3.number_input(
            "Column number",
            min_value=1,
            max_value=len(cols) + 1,
            value=len(cols) + 1,
            key=f"addcol_pos_{i}"
        )

        variable_names.append(name)
        variable_values.append(value)
        column_numbers.append(colnum)

    # Step 2 Next button — closes Step 2 and returns inputs
    if st.button("Next", key="addcols_step2"):
        st.session_state.addColsStep2_active = False

        # Clean empty names
        cleaned = [
            (n.strip(), v, c)
            for n, v, c in zip(variable_names, variable_values, column_numbers)
            if n.strip() != ""
        ]

        if not cleaned:
            st.warning("No valid columns entered. Nothing will be added.")
            return {}

        names, values, positions = zip(*cleaned)

        return {
            "variable_names": list(names),
            "values": list(values),
            "columns": list(positions)
        }

    return None