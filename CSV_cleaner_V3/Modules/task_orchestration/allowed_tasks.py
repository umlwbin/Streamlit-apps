# Modules/task_orchestration/allowed_tasks.py

import streamlit as st
from Modules.task_orchestration.tasks import TASKS


def get_allowed_tasks():
    """
    Determine which tasks are allowed based on the current state.
    For example: if a file is non-rectangular, only allow metadata removal.
    """

    non_rectangular = bool(st.session_state.get("non_rectangular_files"))

    if non_rectangular:
        return ["Remove Metadata Rows"]

    return list(TASKS.keys())
