import streamlit as st
from Modules.task_orchestration.tasks import TASK_DICT
from Modules.utils.ui_utils import big_caption


def what_to_do_widgets(allowed_tasks=None):
    """
    Display a task selector dropdown.

    Parameters
    ----------
    allowed_tasks : list[str] or None
        If provided, only these tasks will appear in the dropdown.
        If None, all tasks from TASK_DICT are shown.
    """

    # Determine which tasks to show
    if allowed_tasks is None:
        task_names = list(TASK_DICT.keys())
    else:
        # Filter to only allowed tasks, preserving order
        task_names = [t for t in TASK_DICT.keys() if t in allowed_tasks]

    selected = st.selectbox("Choose an option", ["Choose an option"] + task_names)

    if selected != "Choose an option":
        task = TASK_DICT[selected]
        description = task.description
        if description:
            big_caption(description)

    return selected
