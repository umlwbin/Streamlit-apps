import streamlit as st

def workflow_steps():
    """
    Subtle breadcrumb-style step indicator for:
    Upload → Select Task → Apply → Download
    """

    # Determine progress
    uploaded = bool(st.session_state.get("current_data"))
    task_applied = st.session_state.get("task_applied", False)

    # Step states
    step1 = "active" if not uploaded else "done"
    step2 = "active" if uploaded and not task_applied else ("done" if task_applied else "inactive")
    step3 = "active" if task_applied else "inactive"
    step4 = "active" if task_applied else "inactive"

    # CSS
    st.markdown("""
        <style>
        .steps-container {
            display: flex;
            gap: 0.6rem;
            font-size: 0.85rem;
            margin: 0.4rem 0 1rem 0;
            opacity: 0.95;
        }
        .step {
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            border: 1px solid rgba(0,0,0,0.15);
            background: rgba(0,0,0,0.03);
            color: #555;
        }
        .step.active {
            background: #e9f5ff;
            border-color: #7bb8f0;
            color: #0b6cbf;
            font-weight: 600;
        }
        .step.done {
            background: #e8f7e8;
            border-color: #7ac27a;
            color: #2d7a2d;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render steps
    st.markdown(f"""
        <div class="steps-container">
            <div class="step {step1}">📁 Upload</div>
            <div class="step {step2}">🧰 Select Task</div>
            <div class="step {step3}">⚙️ Apply</div>
            <div class="step {step4}">⬇️ Download</div>
        </div>
    """, unsafe_allow_html=True)