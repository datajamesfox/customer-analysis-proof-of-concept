import streamlit as st
from PIL import Image
from authentication import login_form, logout_button
import snowflake_session
import pandas as pd
import datetime
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Consumer Corp Data & Analytics: Customer Spend Dashboard",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initiate Session Variables
if 'genderFilter' not in st.session_state:
    st.session_state.genderFilter = 'All'
if 'dateRange' not in st.session_state:
    st.session_state.dateRange = (datetime.datetime(
        2022, 7, 1), datetime.datetime(2022, 10, 18))

# Sidebar Setup
with st.sidebar:
    st.markdown("## 📈 Customer Spend Dashboard")
    st.write("Customer Spend Analytics Page. Understand socio-economic groupings and trends from transaction data.")
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
    imageTitle = Image.open('.\images\Customer Analytics Title.png')
    st.image(imageTitle)
with colt3:
    ''
# Login Form
login_form()

# Page Elements if Login = Success
if st.session_state.authenication == True:

    # Session
    session = snowflake_session.create_session()

    # Filter Functions
    def gender_filter():
        if st.session_state.genderFilter == "All":
            return "where gender = 'M' or gender = 'F'"
        elif st.session_state.genderFilter == "Male":
            return "where gender = 'M'"
        elif st.session_state.genderFilter == "Female":
            return "where gender = 'F'"

    def date_range():
        try:
            input_str = str(st.session_state.dateRange)
            # Evaluate the string as a Python expression
            start_date, end_date = eval(input_str)
            output_str = "and transaction_date <= DATE('{}') and transaction_date >= DATE('{}')".format(
                end_date.strftime('%Y-%m-%d'),
                start_date.strftime('%Y-%m-%d'))
            return output_str
        except:
            start_date = datetime.date(2022, 7, 1)
            end_date = datetime.date(2022, 10, 18)
            output_str = "and transaction_date <= DATE('{}') and transaction_date >= DATE('{}')".format(
                end_date.strftime('%Y-%m-%d'),
                start_date.strftime('%Y-%m-%d'))
            return output_str

    # Filter Variables
    gender = gender_filter()
    date = date_range()

    # BAN Functions

    def total_spend():
        df_total_spend = session.sql("select \
                                        sum(amount) as amount \
                                     from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                     + gender + date).collect()
        df_total_spend = pd.DataFrame(df_total_spend)
        return df_total_spend.iloc[0]

    def total_transactions():
        df_total_transactions = session.sql("select \
                                        count(TRANSACTION_REFERENCE) as count \
                                     from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                            + gender + date).collect()
        df_total_transactions = pd.DataFrame(df_total_transactions)
        return df_total_transactions.iloc[0]

    def spend_per_transaction():
        df_spt = session.sql("select \
                                    to_number(div0(sum(amount),count(TRANSACTION_REFERENCE))) as spt \
                                     from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                             + gender + date).collect()
        df_spt = pd.DataFrame(df_spt)
        return df_spt.iloc[0]

    # Charts
    def weekly_trend():
        df_weekly_trend = session.sql("select  \
                                \
                                date_trunc('WEEK', transaction_date) as TDATE_WEEKLY, \
                                sum(amount) as amount \
                            from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                      + gender + date +
                                      " group by tdate_weekly \
                            order by TDATE_WEEKLY;").collect()
        df_weekly_trend = pd.DataFrame(df_weekly_trend)
        fig = px.line(df_weekly_trend, x="TDATE_WEEKLY", y="AMOUNT")
        fig.update_layout(height=400)
        fig.update_traces(line_color='#FFD600')
        st.plotly_chart(fig, use_container_width=True)
        # return st.dataframe(df_weekly_trend)

    def age_salary():
        df_age_salary = session.sql("select \
                                        salary_band,\
                                        age_band,\
                                        to_number(avg(sq.amount)) as AMOUNT\
                                    from \
                                        (select \
                                            salary_band,\
                                            age_band,\
                                            sum(amount) as amount,\
                                            date_trunc('WEEK', transaction_date) as tdate\
                                        from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                    + gender + date +
                                    " group by user_reference, salary_band, tdate, age_band\
                                    ) sq\
                                    group by salary_band, age_band\
                                    order by salary_band;").collect()
        df_age_salary = pd.DataFrame(df_age_salary)
        fig = px.scatter(df_age_salary, x='AGE_BAND', y='SALARY_BAND', size="AMOUNT",
                         category_orders={'AGE_BAND': ['35-39', '45-49', '50-54']})
        fig.update_layout(height=400)
        fig.update_traces(marker_color='#FFD600')
        st.plotly_chart(fig, use_container_width=True)

    def categories():
        df_categories = session.sql("SELECT\
                                CATEGORY, \
                                sum(AMOUNT) as AMOUNT  \
                            from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                    + gender + date +
                                    " group by CATEGORY \
                            having sum(AMOUNT) >400 \
                            order by AMOUNT asc").collect()
        df_categories = pd.DataFrame(df_categories)
        fig = px.bar(df_categories, x="AMOUNT", y="CATEGORY", orientation='h')
        fig.update_layout(height=400)
        fig.update_traces(marker_color='#FFD600')
        st.plotly_chart(fig, use_container_width=True)

    def day_of_week_spend():
        df_dow_spend = session.sql("select \
                                    DAYNAME(transaction_date) as DOW, \
                                    avg(amount) as AMOUNT, \
                                    salary_band \
                                from CUSTOMER_DATA.PUBLIC.CUSTOMER_SOCIO_ECO "
                                   + gender + date +
                                   "  group by salary_band, DOW \
                                order by SALARY_BAND asc;").collect()
        df_dow_spend = pd.DataFrame(df_dow_spend)
        fig = px.histogram(df_dow_spend, x="DOW", y="AMOUNT", color='SALARY_BAND', color_discrete_sequence=[
                           '#FFD600', '#ffb100', '#ffa100'], barmode='group', category_orders={'DOW': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']})
        fig.update_layout(height=400)
        # fig.update_traces(marker_color='#FFD600')
        st.plotly_chart(fig, use_container_width=True)

    # Page Elements

    # BAN variable

    totalSpend = total_spend()
    totalTransactions = total_transactions()
    spendPerTxn = spend_per_transaction()

    # BANS
    st.write('')
    col3, col4, col5 = st.columns(3)
    with col3:
        col3a, col3b, col3c = st.columns([2, 5, 1])
        with col3a:
            st.write('')
        with col3b:
            st.metric('Total Spend ($)', totalSpend)
        with col3c:
            st.write('')
    with col4:
        col4a, col4b, col4c = st.columns([2, 5, 1])
        with col4a:
            st.write('')
        with col4b:
            st.metric('No. of Transactions', totalTransactions)
        with col4c:
            st.write('')
    with col5:
        col5a, col5b, col5c = st.columns([2, 5, 1])
        with col5a:
            st.write('')
        with col5b:
            st.metric('Avg Spend/Txn ($)', spendPerTxn)
        with col5c:
            st.write('')

    tab1, tab2, tab3, tab4 = st.tabs(["Spend Over Time", "Day of Week Spending",
                                     "Average Weekly Spend by Age & Salary Bands", "Spend by Category"])
    with tab1:
        weekly_trend()
    with tab2:
        day_of_week_spend()
    with tab3:
        age_salary()
    with tab4:
        categories()

    with st.expander("Filters", expanded=False):
        cole1, cole2 = st.columns([1, 2])
        with cole1:
            st.selectbox('Gender', ['All', 'Male',
                         'Female'], key='genderFilter')
        with cole2:
            try:
                st.date_input("Date Range", (datetime.datetime(
                    2022, 7, 1), datetime.datetime(2022, 10, 18)), key='dateRange')
            except:
                st.error("Please select an end date")

    # Logout
    col1, col2 = st.columns(2)
    with col1:
        logout_button()
    with col2:
        st.write('')
