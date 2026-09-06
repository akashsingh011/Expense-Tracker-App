import streamlit as st


def timed_message(type: str, message: str):
    """Show a success/error/info message with a close (x) button."""

    key = f"msg_visible_{message[:20]}"

    if key not in st.session_state:
        st.session_state[key] = True

    if st.session_state[key]:
        col1, col2 = st.columns([20, 1])

        with col1:
            if type == "success":
                st.success(message)
            elif type == "error":
                st.error(message)
            elif type == "info":
                st.info(message)

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✕", key=f"close_{key}"):
                st.session_state[key] = False
                st.rerun()