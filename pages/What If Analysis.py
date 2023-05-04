import streamlit as st
from PIL import Image
from authentication import login_form, logout_button
import snowflake_session
import pandas as pd
import plotly.graph_objects as go


# Page Config
st.set_page_config(
    page_title="Consumer Corp Data & Analytics: What If Analysis",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar Setup
with st.sidebar:
    st.markdown("## 🎯 What If Analysis")
    st.write("Use custom scenarios to explore the potential market capture of targeted advertising or sales outreach.")
    st.write("")
    st.markdown("### About")
    st.write("This app has been created for the 2023 Summit Hackathon. Please note that the data provided is a sample, and this app version is a proof of concept for demonstration purposes only.")
    st.markdown("Utilizes [UK Row-level Transaction Data - Sample](https://app.snowflake.com/marketplace/listing/GZSVZF0IXW/clearscore-technology-ltd-uk-row-level-transaction-data-sample) from the Snowflake Marketplace")
    st.write("")
    st.markdown("### Help")
    st.write("Login to view app elements.")
    st.markdown("**Username**: *user1*")
    st.markdown("**Password**: *qwerty123*")
    for x in range(4):
        st.write("")
    st.markdown("Created by: **James Fox**")
    cols1, cols2, cols3 = st.columns(3)
    with cols1:
        st.markdown("[Twitter](https://twitter.com/jameskalfox)")
    with cols2:
        st.markdown("[Linkedin](https://www.linkedin.com/in/jtf)")
    with cols3:
        st.markdown("[Github](https://github.com/jameskalfox)")

# Title Image
colt1, colt2, colt3 = st.columns([1, 20, 1])
with colt1:
    ''
with colt2:
    imageTitle = Image.open('..\\Impact Title.png')
    st.image(imageTitle)
with colt3:
    ''

if 'age1' not in st.session_state:
    st.session_state.age1 = {0: "30", 1: "60"}
if 'amount1' not in st.session_state:
    st.session_state.amount1 = 20
if 'cat1' not in st.session_state:
    st.session_state.cat1 = "Food, Groceries, Household"
if 'age2' not in st.session_state:
    st.session_state.age2 = {0: "20", 1: "50"}
if 'amount2' not in st.session_state:
    st.session_state.amount2 = 70
if 'cat2' not in st.session_state:
    st.session_state.cat2 = "Enjoyment"

# Login Form
login_form()

if st.session_state.authenication == True:

    # Session
    session = snowflake_session.create_session()

    @st.cache_data
    def categoryList():
        df_category_list = session.sql("select category, sum(amount) as amount\
                                        from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO \
                                        group by category \
                                        order by amount desc;").collect()
        df_category_list = pd.DataFrame(df_category_list)[
            'CATEGORY'].values.tolist()
        return df_category_list

    category_list = categoryList()

    def sql1():
        amount1 = str(st.session_state.amount1)
        category1 = str(st.session_state.cat1)
        df = session.sql("select  \
                            count(transaction_reference) as total_transactions, \
                            (select count(*) \
                            from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO \
                            where age_min > " + st.session_state.age1[0] + " and age_max < " + st.session_state.age1[1] +
                         " and amount < " + amount1 +
                         " and category = '" + category1 + "') as param_transactions, \
                            to_number(param_transactions/total_transactions*100, 38,2) \
                        from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO;").collect()
        df = pd.DataFrame(df)
        return df.iloc[0][2]

    def sql2():
        amount2 = str(st.session_state.amount2)
        category2 = str(st.session_state.cat2)
        df = session.sql("select  \
                            count(transaction_reference) as total_transactions, \
                            (select count(*) \
                            from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO \
                            where age_min > " + st.session_state.age2[0] + " and age_max < " + st.session_state.age2[1] +
                         " and amount < " + amount2 +
                         " and category = '" + category2 + "') as param_transactions, \
                            to_number(param_transactions/total_transactions*100, 38,2) \
                        from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO;").collect()
        df = pd.DataFrame(df)
        return df.iloc[0][2]

    gauge_1_metric = sql1()
    gauge_2_metric = sql2()

    def scen1():

        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=gauge_1_metric,
            number={'suffix': "%"},
            mode="gauge+number",
            title={'text': ""},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': '#FFD600'},
                   'steps': [
                {'range': [80, 100], 'color': "#FFF5BE"},
                {'range': [50, 80], 'color': "#FEF9E2"}]}))

        fig.update_layout(height=200, margin={'t': 30, 'l': 30, 'b': 30, 'r': 30}, font={
                          'color': "#0B014D", 'family': "Arial"})

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Scenario 1", expanded=True):

            st.select_slider(
                'Age Range',
                options=['0', '10', '20', '30', '40', '50', '60', '70'],
                value=('30', '60'), key='age1')

            st.slider('Single Transaction Limit', min_value=0,
                      max_value=100, value=int(20),  key='amount1')

            st.selectbox('Category:', category_list, index=5, key='cat1')

    def scen2():

        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=gauge_2_metric,
            number={'suffix': "%"},
            mode="gauge+number",
            title={'text': ""},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': '#FFD600'},
                   'steps': [
                {'range': [80, 100], 'color': "#FFF5BE"},
                {'range': [50, 80], 'color': "#FEF9E2"}]}))

        fig.update_layout(height=200, margin={'t': 30, 'l': 30, 'b': 30, 'r': 30}, font={
                          'color': "#0B014D", 'family': "Arial"})

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Scenario 2", expanded=True):

            st.select_slider(
                'Age Range',
                options=['0', '10', '20', '30', '40', '50', '60', '70'],
                value=('20', '50'), key='age2')

            st.slider('Single Transaction Limit', min_value=0,
                      max_value=100, value=int(70),  key='amount2')

            st.selectbox('Category:', category_list, index=7, key='cat2')

    # Page Elements
    ''
    st.markdown("##### Use scenarios to estimate % of market capture.")
    st.markdown(
        "*Market capture based on percentage of individual transactions within the scenario parameters.*")

    col1, col2, col3 = st.columns([5, 1, 5], gap="small")
    with col1:
        scen1()
    with col2:
        ''
    with col3:
        scen2()

    # Logout
    col4, col5 = st.columns(2)
    with col4:
        logout_button()
    with col5:
        st.write('')
