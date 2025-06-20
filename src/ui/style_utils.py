import os
import base64
import streamlit as st
import toml


def get_base64_encoded_image(image_path):
    """Convert an image file to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_theme_colors():
    """Load theme colors from config.toml file"""
    try:
        # Path to config.toml relative to this file
        config_path = os.path.join(os.path.dirname(__file__), ".streamlit", "config.toml")
        
        if os.path.exists(config_path):
            config = toml.load(config_path)
            # Return theme colors if they exist
            if "theme" in config:
                return config["theme"]
    except Exception as e:
        st.error(f"Error loading config.toml: {e}")
    
    # Default colors if config.toml can't be loaded
    return {
        "primaryColor": "#30577a",
        "backgroundColor": "#feffff",
        "secondaryBackgroundColor": "#d6e3e4",
        "textColor": "#163d66",
        "font": "sans serif"
    }

def load_css():
    """Load all custom CSS styling for the application"""
    # Get theme colors from  config.toml
    theme = get_theme_colors()

    # Path to the law_logo image
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "law_logo.png")
    
    # Apply the background image and other styling
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('data:image/png;base64,{get_base64_encoded_image(logo_path)}');
        background-size: 20%;
        background-position: bottom 35px right;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-color: {theme["backgroundColor"]};
        opacity: 0.8; 
    }}
    
    .signup-modal {{
        background-color: {theme["primaryColor"]};
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }}
    
    .signup-modal h3 {{
        color: {theme["backgroundColor"]};
        font-weight: 600;
        margin-bottom: 15px;
    }}

    .about-modal {{
        background-color: {theme["secondaryBackgroundColor"]};
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {theme["primaryColor"]};
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .about-modal h2 {{
        color: {theme["primaryColor"]};
        margin-bottom: 15px;
    }}

    </style>
    """, unsafe_allow_html=True)