import streamlit as st


def metric_card(label, value, delta=None, help_text=None):
    """
    Display a metric card using Streamlit's st.metric with custom styling.

    Args:
        label (str): The label of the metric
        value (str or int or float): The value to display
        delta (str or int or float, optional): The delta value to display
        help_text (str, optional): Help text to display on hover
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def indicator_card(title, value, prefix="", suffix=""):
    """
    Display an indicator card using custom HTML and CSS.

    Args:
        title (str): The title of the indicator
        value (str or int or float): The value to display
        prefix (str, optional): Text to display before the value
        suffix (str, optional): Text to display after the value
    """
    # Using the dashboard-card class from CSS
    html = f"""
    <div class="dashboard-card">
        <h3>{title}</h3>
        <h1>{prefix}{value}{suffix}</h1>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)