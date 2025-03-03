import streamlit as st
import plotly.graph_objects as go
from components.point_fitting import point_fitting_interface
from components.direct_params import direct_params_interface
from components.guided_selection import guided_selection_interface
from components.mle_fitting import mle_fitting_interface
from components.auth import login_signup, logout
from utils.curve_storage import initialize_storage, get_saved_curves, delete_curve
from utils.weibull_functions import generate_weibull_curve
from utils.export import export_curve_data, get_csv_download, get_excel_download

def display_curve_comparison(curves):
    """Display comparison of selected curves."""
    st.title("Compare Curves")
    st.write("Select multiple curves to compare their distributions.")

    if not curves:
        st.write("No curves available for comparison.")
        return

    # Create multiselect for curve selection
    curve_names = [curve['name'] for curve in curves]
    selected_curves = st.multiselect(
        "Select curves to compare",
        options=curve_names,
        default=curve_names[0] if curve_names else None
    )

    if not selected_curves:
        st.write("Please select at least one curve to display.")
        return

    # Distribution type selector
    curve_type = st.radio(
        "Distribution Type",
        [
            "CDF (Cumulative Distribution Function)", 
            "PDF (Probability Density Function)",
            "Hazard Function (Failure Rate)"
        ],
        index=0,  # Default to CDF
        key="comparison_dist_type"
    )
    curve_type = "cdf" if "CDF" in curve_type else "pdf" if "PDF" in curve_type else "hazard"

    # Create comparison plot
    fig = go.Figure()

    # Plot selected curves
    for curve_name in selected_curves:
        curve_data = next(curve for curve in curves if curve['name'] == curve_name)
        x_curve, y_curve = generate_weibull_curve(
            curve_data['shape'],
            curve_data['scale'],
            curve_type=curve_type
        )
        fig.add_trace(go.Scatter(
            x=x_curve,
            y=y_curve,
            name=f"{curve_name} (k={curve_data['shape']:.2f}, λ={curve_data['scale']:.2f})",
            line=dict(width=2)
        ))

    y_axis_title = {
        'cdf': "Cumulative Probability",
        'pdf': "Probability Density",
        'hazard': "Hazard Rate (Failures per Unit Time)"
    }[curve_type]

    fig.update_layout(
        title=f"Weibull {curve_type.upper()} Distribution Comparison",
        xaxis_title="Time",
        yaxis_title=y_axis_title,
        showlegend=True,
        width=800,
        height=500,
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
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )

    st.plotly_chart(fig)

def main():
    st.set_page_config(
        page_title="Asset Life Model",
        page_icon="📈",
        layout="wide"
    )

    # Initialize storage
    initialize_storage()

    # Authentication
    if not st.session_state.get("user_id") and not st.session_state.get("is_guest"):
        login_signup()
        # Add footer even on login page
        st.markdown("""
        <div style='position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 0.8em;'>
            Created by <a href='https://www.linkedin.com/in/philjette/' target='_blank'>Philippe Jette</a>
        </div>
        """, unsafe_allow_html=True)
        return

    # Show logout button in sidebar
    logout()

    # Sidebar description
    st.sidebar.markdown("### Model the relationship between asset age and failure probability")

    if st.session_state.get("is_guest"):
        st.sidebar.warning("⚠️ Guest Mode: Save and download features are disabled. Log in to access all features.")

    # Navigation
    pages = ["Point-based fit", "Direct parameter fit", "Guided fit", "Import from CSV (MLE)"]

    # Add Compare Curves option for logged-in users
    if not st.session_state.get("is_guest"):
        st.sidebar.markdown("---")  # Add separator
        pages.append("Compare Curves")

    selected_page = st.sidebar.radio("Navigation", pages)

    # Display selected interface
    if selected_page == "Point-based fit":
        point_fitting_interface()
    elif selected_page == "Direct parameter fit":
        direct_params_interface()
    elif selected_page == "Guided fit":
        guided_selection_interface()
    elif selected_page == "Import from CSV (MLE)":
        mle_fitting_interface()
    elif selected_page == "Compare Curves":
        curves = get_saved_curves(st.session_state.user_id)
        display_curve_comparison(curves)

    # Add footer
    st.markdown("""
    <div style='position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 0.8em;'>
        Created by <a href='https://www.linkedin.com/in/philjette/' target='_blank'>Philippe Jette</a>
    </div>
    """, unsafe_allow_html=True)

    # Show saved curves section only for logged-in users
    if not st.session_state.get("is_guest"):
        st.markdown("---")
        st.subheader("Your Saved Curves")
        curves = get_saved_curves(st.session_state.user_id)

        if not curves:
            st.write("No curves saved yet.")
        else:
            for curve in curves:
                with st.expander(f"{curve['name']} ({curve['timestamp']})"):
                    st.write(f"Description: {curve['description']}")
                    st.write(f"Method: {curve['method']}")
                    st.write(f"Shape (k): {curve['shape']:.3f}")
                    st.write(f"Scale (λ): {curve['scale']:.3f}")

                    # Update the saved curves plotting section to include hazard function
                    curve_type = st.radio(
                        "View Distribution Type:", 
                        [
                            "CDF (Cumulative Distribution Function)", 
                            "PDF (Probability Density Function)",
                            "Hazard Function (Failure Rate)"
                        ],
                        key=f"dist_type_{curve['name']}"
                    )
                    curve_type = "cdf" if "CDF" in curve_type else "pdf" if "PDF" in curve_type else "hazard"

                    # Generate and show curve
                    x_curve, y_curve = generate_weibull_curve(
                        curve['shape'], 
                        curve['scale'], 
                        curve_type=curve_type
                    )
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x_curve, y=y_curve))

                    y_axis_title = {
                        'cdf': "Cumulative Probability",
                        'pdf': "Probability Density",
                        'hazard': "Hazard Rate (Failures per Unit Time)"
                    }[curve_type]

                    fig.update_layout(
                        title=f"Saved Weibull {curve_type.upper()} Distribution",
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

                    # Export options
                    col1, col2, col3 = st.columns(3)

                    # Generate data for export
                    export_type = st.radio(
                        "Export curve type:", 
                        ["CDF only", "Both PDF and CDF"],
                        key=f"export_type_{curve['name']}"
                    )

                    df = export_curve_data(
                        curve['shape'], 
                        curve['scale'], 
                        curve_type='both' if export_type == "Both PDF and CDF" else 'cdf'
                    )

                    with col1:
                        csv_data, csv_filename = get_csv_download(df, f"weibull_curve_{curve['name']}")
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=csv_filename,
                            mime="text/csv",
                            key=f"csv_{curve['name']}"
                        )

                    with col2:
                        excel_data, excel_filename = get_excel_download(df, f"weibull_curve_{curve['name']}")
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"excel_{curve['name']}"
                        )

                    with col3:
                        # Add delete button
                        if st.button("Delete Curve", key=f"delete_{curve['name']}", type="secondary"):
                            success, message = delete_curve(curve['name'], st.session_state.user_id)
                            if success:
                                st.success(message)
                                st.rerun()  # Refresh the page to update the curve list
                            else:
                                st.error(message)

if __name__ == "__main__":
    main()