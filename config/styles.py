# config/styles.py
"""CSS styles and page configuration for LodCORE app."""

import streamlit as st

CSS_STYLES = """
<style>
:root {
    --color-slate: #3D517B;
    --color-primary: #568EE2;
    --color-navy: #051C33;
    --color-teal: #6FB5BA;
    --color-sand: #DFD1B6;
    --color-lilac: #A59FD0;
    --color-error: #C33241;
    --color-success: #377F86;
    --color-warning: #C35309;
}

/* Light mode background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, var(--background-color) 0%, var(--color-sand) 100%);
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d29 100%);
    }
}

/* ===== RESPONSIVE LAYOUT ===== */

/* Mobile: Single column, larger touch targets */
@media (max-width: 767px) {
    .main-header {
        font-size: 1.8rem !important;
    }
    
    .municipality-name {
        font-size: 1.2rem !important;
    }
    
    .score-badge {
        font-size: 0.8rem !important;
        padding: 0.4rem 0.8rem !important;
    }
    
    /* Force single column for municipality cards */
    [data-testid="column"] {
        width: 100% !important;
        flex: 0 0 100% !important;
    }
    
    /* Larger buttons for touch */
    .stButton > button {
        padding: 0.6rem 1.2rem !important;
        font-size: 1rem !important;
    }
    
    /* Stack comparison cards vertically */
    .comparison-header {
        font-size: 0.9rem !important;
    }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 1023px) {
    .main-header {
        font-size: 2rem !important;
    }
    
    .municipality-name {
        font-size: 1.3rem !important;
    }
    
    /* 2-column layout for comparison view */
    [data-testid="column"]:nth-child(n+3) {
        margin-top: 1rem;
    }
}

/* Desktop: Full layout (>1024px) - default styles apply */

.main-header {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--color-primary), var(--color-slate));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 1rem;
}

.tagline {
    color: var(--text-color);
    font-style: italic;
    text-align: center;
    margin-top: 0;
    margin-bottom: 1.5rem;
    opacity: 0.8;
}

.score-badge {
    background: linear-gradient(90deg, var(--color-primary), var(--color-teal));
    color: #ffffff !important;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-weight: 600;
    display: inline-block;
    margin: 0.3rem 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    font-size: 0.9rem;
}

.municipality-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: 0.8rem;
}

.detail-panel {
    background: var(--background-color);
    border: 1px solid var(--color-primary);
    border-radius: 15px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.concept-icon {
    font-size: 1.3rem;
    margin-right: 0.5rem;
}

/* Buttons - theme aware with white text */
.stButton > button {
    background: linear-gradient(90deg, var(--color-primary), var(--color-teal)) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 999px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
    color: #ffffff !important;
}
.stButton > button:active,
.stButton > button:focus {
    color: #ffffff !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(90deg, var(--color-success), var(--color-teal)) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 999px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    color: #ffffff !important;
}

.comparison-header {
    background: var(--color-slate);
    color: #ffffff;
    padding: 0.8rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
    font-weight: 600;
}

.plot-container {
    border-radius: 16px;
    overflow: hidden;
}

/* Radio buttons - ensure visibility */
[data-testid="stRadio"] label {
    color: var(--text-color) !important;
}

/* Selectbox - ensure visibility */
[data-testid="stSelectbox"] label {
    color: var(--text-color) !important;
}

/* Number input - ensure visibility */
[data-testid="stNumberInput"] label {
    color: var(--text-color) !important;
}

/* Slider - ensure visibility */
[data-testid="stSlider"] label {
    color: var(--text-color) !important;
}

/* Multiselect - ensure visibility */
[data-testid="stMultiSelect"] label {
    color: var(--text-color) !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--color-navy) 0%, #1a1d29 100%);
}

[data-testid="stSidebar"] * {
    color: #F9FAFB !important;
}

/* Sidebar selectbox - fix selected option visibility */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #F9FAFB !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #F9FAFB !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #F9FAFB !important;
}

/* Sidebar multiselect */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: var(--color-primary) !important;
    color: #ffffff !important;
}

/* Sidebar number input - fix all elements */
[data-testid="stSidebar"] input[type="number"] {
    color: #051C33 !important;
    background-color: #F9FAFB !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    color: #F9FAFB !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] svg {
    fill: #F9FAFB !important;
}

/* Sidebar slider */
[data-testid="stSidebar"] [data-baseweb="slider"] {
    color: #F9FAFB !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(90deg, var(--color-primary), var(--color-teal)) !important;
    color: #ffffff !important;
}

/* Expander - theme aware */
[data-testid="stExpander"] {
    background: var(--background-color);
    border: 1px solid var(--color-primary);
    border-radius: 10px;
}

/* Dataframe - ensure readability */
[data-testid="stDataFrame"] {
    background: var(--background-color);
}

/* Metric - theme aware */
[data-testid="stMetric"] {
    background: var(--background-color);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(86, 142, 226, 0.3);
}

/* Back to top button */
.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: linear-gradient(90deg, var(--color-primary), var(--color-teal)) !important;
    color: #ffffff !important;
    border: none;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    text-decoration: none !important;
    border-bottom: none !important;
    opacity: 0;
    pointer-events: none;
    animation: fadeIn 0.3s ease-in-out 3s forwards;
}

@keyframes fadeIn {
    to {
        opacity: 1;
        pointer-events: auto;
    }
}

.back-to-top:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

/* Mobile adjustments */
@media (max-width: 767px) {
    .back-to-top {
        bottom: 1rem;
        right: 1rem;
        width: 48px;
        height: 48px;
        font-size: 20px;
    }
}

/* Demographics stacked bar */
.demographics-bar {
    display: flex;
    height: 30px;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.demographics-bar > div {
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 11px;
    font-weight: 600;
    transition: opacity 0.2s ease;
}

.demographics-bar > div:hover {
    opacity: 0.85;
}

.demographics-legend {
    font-size: 13px;
    color: #666;
    margin-top: 0.25rem;
    font-weight: 500;
}

.demographics-legend span {
    margin-right: 0.75rem;
}


</style>
"""


def apply_styles() -> None:
    """Apply page configuration and custom CSS styles."""
    st.set_page_config(
        page_title="Living on the Edge",
        page_icon=":material/home:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
