import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px



def what_kind_of_files_widget():
    st.markdown('Depending on the structure of the provincial file you have, we have provided several cleaning options. Please select skip step if you would not like to perform a task.')

    

