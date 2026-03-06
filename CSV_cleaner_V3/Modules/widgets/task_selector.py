import streamlit as st
from Modules import tasks
from Modules.ui_utils import big_caption

def what_to_do_widgets(allowed_tasks=None):
    """
    Display a task selector dropdown.

    Parameters
    ----------
    allowed_tasks : list[str] or None
        If provided, only these tasks will appear in the dropdown.
        If None, all tasks from define_task_functions() are shown.
    """

    task_dict = tasks.define_task_functions()

    # Determine which tasks to show
    if allowed_tasks is None:
        task_names = list(task_dict.keys())
    else:
        # Filter to only allowed tasks, preserving order
        task_names = [t for t in task_dict.keys() if t in allowed_tasks]

    selected = st.selectbox("Choose an option", ["Choose an option"] + task_names)

    if selected != "Choose an option":
        description = task_dict[selected].get("description", "")
        if description:
            big_caption(description)

    return selected
