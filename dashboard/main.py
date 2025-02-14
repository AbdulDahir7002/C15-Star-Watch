import streamlit as st
import logging
import Home
import Page1
import Page2
import Subscriber


def define_logger():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler("dashboard.log")])
    return logging.getLogger()


logger = define_logger()

st.set_page_config(page_title="Streamlit Multi-Page Example", layout="wide")

PAGES = {
    "Home": Home,
    "Page 1": Page1,
    "Page 2": Page2,
    "Subscribe": Subscriber
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
logger.info(f"The user has selected {selection}")

page = PAGES[selection]
page.app()
