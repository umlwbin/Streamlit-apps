import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px

#PATHS----------------------------------------------------------------------------------------------------------------------------
#Input_path is where the script and any input files are found, output_path is where the output files are created -the current dir.
#input_path=os.path.abspath(os.curdir)+'/Prov_chem/' #For Streamlit Directory
input_path=os.path.abspath(os.curdir) #For desktop
output_path=os.path.abspath(os.curdir)
#----------------------------------------------------------------------------------------------------------------------------------

def download_or_continue_widgets():
    