"""
Centralized theme configuration for FLUX demos.
Provides a responsive console/dark theme for both Gradio and Streamlit interfaces.
"""

# Console theme colors - dark theme with professional appearance
CONSOLE_COLORS = {
    "primary": "#1a1a1a",  # Dark background
    "secondary": "#2d2d2d",  # Slightly lighter background
    "accent": "#00d4ff",  # Bright cyan accent
    "success": "#00ff88",  # Bright green
    "warning": "#ffaa00",  # Orange
    "danger": "#ff4444",  # Red
    "text_primary": "#ffffff",  # White text
    "text_secondary": "#cccccc",  # Light gray text
    "border": "#444444",  # Border color
    "input_bg": "#2d2d2d",  # Input background
    "button_primary": "#00d4ff",  # Primary button
    "button_hover": "#00a8cc",  # Button hover state
}


def get_gradio_theme():
    """
    Returns a Gradio theme configuration with console-style dark theme.
    
    Returns:
        gr.Theme: Configured Gradio theme object
    """
    try:
        import gradio as gr
        
        # Create a custom theme based on the base dark theme
        theme = gr.themes.Base(
            primary_hue=gr.themes.colors.cyan,
            secondary_hue=gr.themes.colors.gray,
            neutral_hue=gr.themes.colors.gray,
            font=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
        ).set(
            # Background colors
            body_background_fill=CONSOLE_COLORS["primary"],
            body_background_fill_dark=CONSOLE_COLORS["primary"],
            background_fill_primary=CONSOLE_COLORS["secondary"],
            background_fill_primary_dark=CONSOLE_COLORS["secondary"],
            background_fill_secondary=CONSOLE_COLORS["primary"],
            background_fill_secondary_dark=CONSOLE_COLORS["primary"],
            # Text colors
            body_text_color=CONSOLE_COLORS["text_primary"],
            body_text_color_dark=CONSOLE_COLORS["text_primary"],
            # Button colors
            button_primary_background_fill=CONSOLE_COLORS["button_primary"],
            button_primary_background_fill_dark=CONSOLE_COLORS["button_primary"],
            button_primary_background_fill_hover=CONSOLE_COLORS["button_hover"],
            button_primary_background_fill_hover_dark=CONSOLE_COLORS["button_hover"],
            button_primary_text_color=CONSOLE_COLORS["primary"],
            button_primary_text_color_dark=CONSOLE_COLORS["primary"],
            # Border colors
            border_color_primary=CONSOLE_COLORS["border"],
            border_color_primary_dark=CONSOLE_COLORS["border"],
            # Input colors
            input_background_fill=CONSOLE_COLORS["input_bg"],
            input_background_fill_dark=CONSOLE_COLORS["input_bg"],
        )
        
        return theme
    except ImportError:
        # Gradio not installed, return None
        return None


def get_streamlit_theme_config():
    """
    Returns Streamlit theme configuration as a dictionary.
    
    This should be set via .streamlit/config.toml or st.set_page_config.
    
    Returns:
        dict: Streamlit theme configuration
    """
    return {
        "primaryColor": CONSOLE_COLORS["accent"],
        "backgroundColor": CONSOLE_COLORS["primary"],
        "secondaryBackgroundColor": CONSOLE_COLORS["secondary"],
        "textColor": CONSOLE_COLORS["text_primary"],
        "font": "monospace",
    }


def get_custom_css_for_streamlit():
    """
    Returns custom CSS for Streamlit to enhance the console theme.
    
    Returns:
        str: CSS string to be injected via st.markdown
    """
    return f"""
    <style>
    /* Console theme for Streamlit */
    .stApp {{
        background-color: {CONSOLE_COLORS["primary"]};
    }}
    
    /* Header styling */
    h1, h2, h3 {{
        color: {CONSOLE_COLORS["text_primary"]} !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: {CONSOLE_COLORS["button_primary"]};
        color: {CONSOLE_COLORS["primary"]};
        border: none;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {CONSOLE_COLORS["button_hover"]};
        box-shadow: 0 0 10px {CONSOLE_COLORS["accent"]}44;
    }}
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {CONSOLE_COLORS["input_bg"]};
        color: {CONSOLE_COLORS["text_primary"]};
        border: 1px solid {CONSOLE_COLORS["border"]};
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* Slider styling */
    .stSlider > div > div > div > div {{
        background-color: {CONSOLE_COLORS["accent"]};
    }}
    
    /* Checkbox styling */
    .stCheckbox > label > div {{
        background-color: {CONSOLE_COLORS["secondary"]};
        border-color: {CONSOLE_COLORS["border"]};
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {CONSOLE_COLORS["secondary"]};
        color: {CONSOLE_COLORS["text_primary"]};
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* File uploader styling */
    .stFileUploader > div > div {{
        background-color: {CONSOLE_COLORS["secondary"]};
        border: 2px dashed {CONSOLE_COLORS["border"]};
    }}
    
    /* Download button styling */
    .stDownloadButton > button {{
        background-color: {CONSOLE_COLORS["success"]};
        color: {CONSOLE_COLORS["primary"]};
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* Info/Warning boxes */
    .stAlert {{
        background-color: {CONSOLE_COLORS["secondary"]};
        border-left: 4px solid {CONSOLE_COLORS["accent"]};
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .stApp {{
            padding: 1rem;
        }}
        
        h1 {{
            font-size: 1.5rem !important;
        }}
        
        .stButton > button {{
            width: 100%;
            margin-bottom: 0.5rem;
        }}
    }}
    
    /* Canvas and image containers */
    .stImage > img,
    canvas {{
        border: 1px solid {CONSOLE_COLORS["border"]};
        border-radius: 4px;
    }}
    </style>
    """


def get_custom_css_for_gradio():
    """
    Returns custom CSS for Gradio to enhance the console theme.
    
    Returns:
        str: CSS string to be used with gr.Blocks(css=...)
    """
    return f"""
    /* Console theme for Gradio */
    .gradio-container {{
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        background-color: {CONSOLE_COLORS["primary"]} !important;
    }}
    
    /* Responsive layout */
    @media (max-width: 768px) {{
        .gradio-container {{
            padding: 1rem !important;
        }}
        
        .gr-button {{
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .gr-form {{
            gap: 0.5rem !important;
        }}
    }}
    
    /* Enhanced button effects */
    .gr-button {{
        transition: all 0.3s ease !important;
        font-weight: bold !important;
    }}
    
    .gr-button:hover {{
        box-shadow: 0 0 15px {CONSOLE_COLORS["accent"]}66 !important;
        transform: translateY(-2px);
    }}
    
    /* Image containers */
    .gr-image {{
        border: 1px solid {CONSOLE_COLORS["border"]} !important;
        border-radius: 4px !important;
    }}
    
    /* Accordion styling */
    .gr-accordion {{
        border: 1px solid {CONSOLE_COLORS["border"]} !important;
    }}
    """
