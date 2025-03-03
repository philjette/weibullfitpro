import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.weibull_functions import fit_weibull_to_points, generate_weibull_curve
from utils.curve_storage import save_curve

def point_fitting_interface():
    """Interface for point-based Weibull fitting."""
    st.subheader("Point-Based Fitting")
    st.write("Enter the age at which you expect specific percentages of assets to have failed.")

    col1, col2 = st.columns(2)

    with col1:
        # Age inputs for specific failure percentages
        st.write("### Asset Failure Ages")
        x1 = st.number_input(
            "At what age do you expect 25% of assets to have failed?",
            min_value=0.1,
            value=1.0,
            help="Enter the age at which 25% of assets are expected to fail"
        )

        x2 = st.number_input(
            "At what age do you expect 50% of assets to have failed?",
            min_value=0.1,
            value=2.0,
            help="Enter the age at which 50% of assets are expected to fail"
        )

        x3 = st.number_input(
            "At what age do you expect 75% of assets to have failed?",
            min_value=0.1,
            value=3.0,
            help="Enter the age at which 75% of assets are expected to fail"
        )

    # Validate age sequence
    if not (x1 <= x2 <= x3):
        st.error("Ages must be in ascending order (25% ≤ 50% ≤ 75%)")
        return

    # Fixed y-values for CDF points
    x_points = np.array([x1, x2, x3])
    y_points = np.array([0.25, 0.50, 0.75])

    # Distribution type selector
    curve_type = st.radio(
        "Distribution Type",
        [
            "CDF (Cumulative Distribution Function)", 
            "PDF (Probability Density Function)",
            "Hazard Function (Failure Rate)"
        ],
        index=0,  # Default to CDF
        key="dist_type"
    )
    curve_type = "cdf" if "CDF" in curve_type else "pdf" if "PDF" in curve_type else "hazard"

    try:
        # Always fit using CDF points
        shape, scale = fit_weibull_to_points(x_points, y_points)

        if shape is None or scale is None:
            st.error("Could not fit Weibull curve to provided points")
            return

        # Display current parameters above the plot
        st.write("### Current Parameters")
        st.write(f"Shape (k): {shape:.3f}")
        st.write(f"Scale (λ): {scale:.3f}")

        # Initialize the plot
        plot_placeholder = st.empty()

        # Initial plot
        fig = go.Figure()

        if curve_type == "cdf":
            fig.add_trace(go.Scatter(
                x=x_points,
                y=y_points,
                mode='markers',
                name='Input Points',
                marker=dict(size=10)
            ))

        # Generate initial curve
        x_curve, y_curve = generate_weibull_curve(shape, scale, curve_type=curve_type)
        fig.add_trace(go.Scatter(
            x=x_curve,
            y=y_curve,
            name='Fitted Weibull',
            line=dict(color='red', width=2)
        ))

        y_axis_title = {
            'cdf': "Cumulative Probability",
            'pdf': "Probability Density",
            'hazard': "Hazard Rate (Failures per Unit Time)"
        }[curve_type]

        fig.update_layout(
            title=f"Weibull {curve_type.upper()} Curve Fit",
            xaxis_title="Time",
            yaxis_title=y_axis_title,
            showlegend=True,
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

        # Display the initial plot
        plot_placeholder.plotly_chart(fig)

        # Fine-tuning sliders below the plot
        st.subheader("Fine-tune Parameters")

        shape_adjusted = st.slider(
            "Adjust Shape Parameter (k)",
            min_value=max(0.1, shape * 0.5),
            max_value=shape * 2.0,
            value=float(shape),
            help="Fine-tune the shape parameter"
        )

        scale_adjusted = st.slider(
            "Adjust Scale Parameter (λ)",
            min_value=max(0.1, scale * 0.5),
            max_value=scale * 2.0,
            value=float(scale),
            help="Fine-tune the scale parameter"
        )

        # Update plot if parameters change
        if shape_adjusted != shape or scale_adjusted != scale:
            # Update curve data
            x_curve, y_curve = generate_weibull_curve(shape_adjusted, scale_adjusted, curve_type=curve_type)
            fig.data = []  # Clear existing traces

            if curve_type == "cdf":
                fig.add_trace(go.Scatter(
                    x=x_points,
                    y=y_points,
                    mode='markers',
                    name='Input Points',
                    marker=dict(size=10)
                ))

            fig.add_trace(go.Scatter(
                x=x_curve,
                y=y_curve,
                name='Fitted Weibull',
                line=dict(color='red', width=2)
            ))

            # Update the plot in place
            plot_placeholder.plotly_chart(fig)

            # Update parameters display
            st.write("### Current Parameters")
            st.write(f"Shape (k): {shape_adjusted:.3f}")
            st.write(f"Scale (λ): {scale_adjusted:.3f}")

        # Only show save functionality for logged-in users
        if not st.session_state.get("is_guest"):
            st.subheader("Save This Curve")
            name = st.text_input("Curve Name")
            description = st.text_area("Description")

            if st.button("Save Curve"):
                success, message = save_curve(
                    name,
                    description,
                    shape_adjusted,
                    scale_adjusted,
                    "Point Fitting",
                    st.session_state.get("user_id")
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

    except Exception as e:
        st.error(f"Error fitting curve: {str(e)}")