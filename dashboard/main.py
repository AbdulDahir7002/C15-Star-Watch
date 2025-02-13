import streamlit as st
import Home
import Page1
import Page2
import Subscriber

st.set_page_config(page_title="Streamlit Multi-Page Example", layout="wide")

PAGES = {
    "Home": Home,
    "Page 1": Page1,
    "Page 2": Page2,
    "Subscribe": Subscriber
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page.app()
