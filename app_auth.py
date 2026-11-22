import hmac

import streamlit as st


def require_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.title("Get or Not?")
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if hmac.compare_digest(password, st.secrets["APP_PASSWORD"]):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()


def logout_button():
    if st.sidebar.button("Log out"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.pop("vectorstore", None)
        st.rerun()
