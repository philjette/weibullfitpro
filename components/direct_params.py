import streamlit as st
import plotly.graph_objects as go
from utils.weibull_functions import generate_weibull_curve, validate_parameters
from utils.curve_storage import save_curve

def direct_params_interface():
    """Interface for direct parameter input."""
    st.subheader("Direct Parameter Input")
    st.write("Enter Weibull parameters directly to generate the curve.")

    col1, col2 = st.columns(2)

    with col1:
        shape = st.number_input(
            "Shape Parameter (k)",
            min_value=0.1,
            value=2.0,
            help="Controls the shape of the distribution. Higher values lead to narrower peaks."
        )

        scale = st.number_input(
            "Scale Parameter (λ)",
            min_value=0.1,
            value=1.0,
            help="Controls the scale of the distribution. Higher values stretch the distribution."
        )

    # Distribution type selector
    curve_type = st.radio(
        "Distribution Type",
        [
            "CDF (Cumulative Distribution Function)", 
            "PDF (Probability Density Function)",
            "Hazard Function (Failure Rate)"
        ],
        index=0,  # Default to CDF
        key="direct_params_dist_type"
    )
    curve_type = "cdf" if "CDF" in curve_type else "pdf" if "PDF" in curve_type else "hazard"

    valid, message = validate_parameters(shape, scale)

    if valid:
        x_curve, y_curve = generate_weibull_curve(shape, scale, curve_type=curve_type)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_curve, y=y_curve))

        y_axis_title = {
            'cdf': "Cumulative Probability",
            'pdf': "Probability Density",
            'hazard': "Hazard Rate (Failures per Unit Time)"
        }[curve_type]

        fig.update_layout(
            title=f"Weibull {curve_type.upper()} Distribution",
            xaxis_title="Time",
            yaxis_title=y_axis_title,
            showlegend=False,
            width=800,
            font=dict(
                size=14,
                family="Arial, sans-serif",
                color="black"
            ),
            xaxis=dict(
                title_font=dict(size=16, family="Arial, sans-serif"),
                tickfont=dict(size=14)
            ),
            yaxis=dict(
                title_font=dict(size=16, family="Arial, sans-serif"),
                tickfont=dict(size=14)
            )
        )

        st.plotly_chart(fig)

        # Only show save functionality for logged-in users
        if not st.session_state.get("is_guest"):
            # Save curve
            st.subheader("Save This Curve")
            name = st.text_input("Curve Name")
            description = st.text_area("Description")

            if st.button("Save Curve"):
                success, message = save_curve(
                    name, 
                    description, 
                    shape, 
                    scale, 
                    "Direct Parameters",
                    st.session_state.get("user_id")
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.error(message)