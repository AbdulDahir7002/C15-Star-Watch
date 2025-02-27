"""Main page running the streamlit app"""
import streamlit as st
import logging
import Home
import Page1
import Page2
import Subscriber
import Unsubscribe


def define_logger():
    """Configures the logger"""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler("logs/dashboard.log")])
    return logging.getLogger()


logger = define_logger()

st.set_page_config(page_title="StarWatch", layout="wide")

if "show_unsubscribe" not in st.session_state:
    st.session_state.show_unsubscribe = False
if "page" not in st.session_state:
    st.session_state.page = "Home"


PAGES = {
    "Home": Home,
    "Forecast": Page1,
    "Trends": Page2,
    "Subscribe": Subscriber
}

if st.session_state.show_unsubscribe:
    PAGES["Unsubscribe"] = Unsubscribe

st.sidebar.markdown(
    """
    <style>
    .sidebar .block-container .stImage{
        display: flex;
        justify-content: center;
        padding_left: auto;
        padding_right: auto;
        width: 75%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.sidebar.image('starwatch_logo.png')
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
logger.info(f"The user has selected {selection}")
st.session_state.page = selection

page = PAGES[st.session_state.page]
page.app()
