import streamlit as st
import copy


def undo_redo_restart_widgets():
    #Butons
    c1,c2, c3,c4=st.columns([0.3,0.3, 0.4, 0.5], vertical_alignment="bottom")
    undo=c1.button("Undo", icon="⏪️")
    redo=c2.button("Redo", icon="⏩️")
    restart=c3.button("Restart Processing", icon='🔄' )

    if undo:
        undo_func()
    if redo:
        redo_func()
    if restart:
        restart_func()


def undo_func():
    if st.session_state.df_history:

        #Turn off everything--------------------------------------
        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False
        #----------------------------------------------------------

        # Move current df list to redo stack
        st.session_state.redo_stack.append(copy.deepcopy(st.session_state.cleaned_df_list))

        # Revert to previous state
        st.session_state.cleaned_df_list = st.session_state.df_history.pop()

    else:

        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False
        st.toast("Nothing to undo!",icon="⚠️")    


def redo_func():

    if st.session_state.redo_stack:

        #Turn off everything--------------------------------------
        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False
        #----------------------------------------------------------

        # Save current dflist to history before redo
        st.session_state.df_history.append(copy.deepcopy(st.session_state.cleaned_df_list))

        # Redo the last undone change
        st.session_state.cleaned_df_list = st.session_state.redo_stack.pop()

    else:
        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False
        st.toast("Nothing to redo!",icon="⚠️")   


def restart_func():
    if st.session_state.df_history:

        #Turn off everything--------------------------------------
        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False
        
        #start of history stack
        st.session_state.cleaned_df_list = copy.deepcopy(st.session_state.df_history[0])

    else:
        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False

        st.toast("Already at the beginning!", icon="⚠️")     