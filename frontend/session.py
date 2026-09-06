import streamlit as st
from streamlit_cookies_controller import CookieController

_controller = CookieController()


def initialize_session():
    if "access_token" not in st.session_state:
        # Try restoring from cookie on first load
        token = _controller.get("access_token")
        st.session_state["access_token"] = token or None

    if "user" not in st.session_state:
        st.session_state["user"] = None


def is_authenticated() -> bool:
    return st.session_state.get("access_token") is not None


def get_token() -> str | None:
    return st.session_state.get("access_token")


def get_user() -> dict | None:
    return st.session_state.get("user")


def login(token: str, user: dict):
    st.session_state["access_token"] = token
    st.session_state["user"] = user
    _controller.set("access_token", token)   # persist to browser


def logout():
    st.session_state["access_token"] = None
    st.session_state["user"] = None
    _controller.remove("access_token")       # clear from browser