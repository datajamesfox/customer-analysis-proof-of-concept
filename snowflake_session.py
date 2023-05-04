import streamlit as st
from snowflake.snowpark import Session


@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets.snowflake).create()
