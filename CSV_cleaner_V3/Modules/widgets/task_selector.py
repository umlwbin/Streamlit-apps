import streamlit as st
from Modules import tasks
from Modules.ui_utils import big_caption

def what_to_do_widgets():
    task_dict = tasks.define_task_functions()
    task_names = list(task_dict.keys())

    selected = st.selectbox("Choose an option", ["Choose an option"] + task_names)

    if selected != "Choose an option":
        description = task_dict[selected].get("description", "")
        if description:
            big_caption(description)

    return selected