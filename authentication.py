import streamlit as st
import time

var = 1


def login_form():
    if 'authenication' not in st.session_state:
        st.session_state.authenication = False
    if st.session_state.authenication == False:
        st.write('')
        login_form = st.empty()
        with login_form.form(key='Login'):
            username = st.text_input('Username', 'user1')
            password = st.text_input('Password', 'qwerty123', type="password")
            submitted = st.form_submit_button("Login")
            if submitted == True and username == 'user1' and password == 'qwerty123':
                with st.spinner('Logging in...'):
                    time.sleep(1.5)
                    st.success('Login Successful')
                    st.session_state.authenication = True
                time.sleep(1)
                login_form.empty()
            elif submitted == True and username == '' and password == '':
                message = st.info('Input username/password')
                time.sleep(1.5)
                message.empty()
            elif submitted == True:
                message = st.warning('Incorrect username/password')
                time.sleep(1.5)
                message.empty()


def logout_button():
    if st.session_state.authenication == True:
        if st.button('Logout'):
            st.session_state.authenication = False
            st.experimental_rerun()
