import streamlit as st
from utils.auth import create_user, authenticate_user, create_access_token
from utils.database import get_db

def login_signup():
    """Handle user authentication interface."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # Add welcome header and description
    st.title("Welcome to Weibull Fit!")
    st.markdown("""
    A powerful statistical modeling application designed to help engineers and reliability professionals analyze asset life and failure probability through advanced Weibull distribution modeling. Create, save, and compare models using various fitting methods, from simple point-based estimation to sophisticated Maximum Likelihood techniques.

    Creating an account enables you to save curves you've created and download them in CSV or XLSX formats.
    """)
    st.markdown("---")

    # Add about section explaining key concepts
    with st.expander("📚 About Statistical Concepts"):
        st.markdown("""
        ### Key Concepts

        #### Weibull Distribution
        A versatile statistical tool used to model the lifetime of assets and predict failure rates. It's particularly useful for reliability engineering and maintenance planning.

        #### Probability Density Function (PDF)
        Shows how likely different failure times are. Think of it as a "probability map" showing which ages are most common for failures to occur.

        #### Cumulative Distribution Function (CDF)
        Shows the total probability of failure up to a certain age. For example, a CDF value of 0.75 at 5 years means there's a 75% chance of failure within the first 5 years.

        #### Hazard Function (Failure Rate)
        Represents the likelihood of immediate failure for an asset that has survived up to a certain age. Useful for understanding how failure risk changes over time.

        #### Maximum Likelihood Estimation (MLE)
        A mathematical method that finds the most likely Weibull parameters to match your actual failure data. It's like finding the best-fitting curve through your data points.
        """)

    st.markdown("---")

    # Add guest mode option
    if st.button("Continue as Guest"):
        st.session_state.user_id = None
        st.session_state.is_guest = True
        st.rerun()

    st.markdown("---")
    st.write("Or create an account to save and download your curves:")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                db = next(get_db())
                user = authenticate_user(email, password, db)
                if user:
                    token = create_access_token({"sub": str(user.id)})
                    st.session_state.user_id = user.id
                    st.session_state.token = token
                    st.session_state.is_guest = False
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")

    with tab2:
        with st.form("signup_form"):
            st.subheader("Sign Up")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")

            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    db = next(get_db())
                    success, message = create_user(new_email, new_password, db)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def logout():
    """Handle user logout."""
    if st.session_state.get("user_id") or st.session_state.get("is_guest"):
        if st.sidebar.button("Logout" if st.session_state.get("user_id") else "Exit Guest Mode"):
            st.session_state.user_id = None
            st.session_state.token = None
            st.session_state.is_guest = False
            st.rerun()