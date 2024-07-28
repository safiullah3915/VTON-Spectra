import streamlit as st
from PIL import Image
from gradio_client import Client, handle_file
import os
import time
import httpx
import auth

# ------- PAGE CONFIGURATION -------
st.set_page_config(layout="wide", page_title="Virtual Try-On")

# ------- USER AUTHENTICATION -------
auth.create_user_table()

def show_signup_page():
    st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #ffffff;'>
            <h1 style='color: #1e90ff; font-family: Montserrat, sans-serif;'>Join the Style Revolution!</h1>
            <p style='font-size: 16px; color: #777;'>Create an account to start your fashion journey</p>
        </div>
        <hr style='margin-top: 20px;'>
    """, unsafe_allow_html=True)
    
    st.subheader("Create New Account")
    name = st.text_input("Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            error = auth.add_user(name, username, password)
            if error:
                st.error(error)
            else:
                st.success("Account created successfully! You are now registered.")
                st.session_state['registered'] = True
                

def show_login_page():
    st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #f9f9f9;'>
            <h1 style='color: #ff6347; font-family: Open Sans, sans-serif;'>VTON By Spectra</h1>
            <p style='font-size: 16px; color: #777;'>Your ultimate virtual fashion try-on experience</p>
        </div>
        <hr style='margin-top: 20px;'>
    """, unsafe_allow_html=True)
    
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = auth.authenticate_user(username, password)
        if user:
            st.session_state['user'] = user
            # Reload the page to reflect the login
            st.rerun()
        else:
            st.error("Username/password is incorrect")

# Login/Signup Page
if 'user' not in st.session_state:
    page = st.sidebar.selectbox("Select Page", ["Login", "Sign Up"])
    if page == "Login":
        show_login_page()
    else:
        show_signup_page()
else:
    user = st.session_state['user']
    st.sidebar.title(f"Welcome {user[1]}")
    if st.sidebar.button("Logout"):
        del st.session_state['user']
        # Reload the page to reflect the logout
        st.rerun()

    # ------- MAIN PAGE BANNER -------
    banner_image = Image.open("banner.png")
    st.image(banner_image, use_column_width=True)
   
    # ------- CONSTANTS -------
    IMAGE_DIMENSION = 300
    IMAGE_CONTAINER_WIDTH = IMAGE_DIMENSION + 50  # Add some padding around the image

    # ------- FUNCTIONS -------
    def save_uploaded_file(uploaded_file):
        """Save the uploaded file to a temporary path."""
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_path

    def try_on(model_image_path, garment_image_path):
        """Process the try-on operation."""
        retries = 3
        for attempt in range(retries):
            try:
                client = Client("yisol/IDM-VTON")
                result = client.predict(
                    dict={"background": handle_file(model_image_path), "layers": [], "composite": None},
                    garm_img=handle_file(garment_image_path),
                    garment_des="Trying on the shirt",
                    is_checked=True,
                    is_checked_crop=False,
                    denoise_steps=30,
                    seed=42,
                    api_name="/tryon"
                )
                return result[0]
            except (httpx.ConnectTimeout, httpx.ReadTimeout):
                if attempt < retries - 1:
                    time.sleep(2)  # wait for 2 seconds before retrying
                else:
                    st.error("Failed to connect to the server. Please try again later.")
                    return None

    def save_image(output_image, save_path):
        """Save the output image to the specified path."""
        output_image.save(save_path)
        st.success("Image saved successfully.")

    # ------- SIDEBAR -------
    st.sidebar.write("## Upload and Process Images")

    # Initialize session state if not already initialized
    if 'output_image' not in st.session_state:
        st.session_state.output_image = None
    if 'model_image_file' not in st.session_state:
        st.session_state.model_image_file = None
    if 'garment_image_file' not in st.session_state:
        st.session_state.garment_image_file = None

    # Select model image
    model_image_file = st.sidebar.file_uploader("Select Model Image", type=["jpeg", "jpg", "png"])
    if model_image_file:
        st.session_state.model_image_file = model_image_file

    # Select garment image
    garment_image_file = st.sidebar.file_uploader("Select Garment Image", type=["jpeg", "jpg", "png"])
    if garment_image_file:
        st.session_state.garment_image_file = garment_image_file

    # ------- MAIN BODY -------
    model_image = None
    garment_image = None
    model_image_path = None
    garment_image_path = None

    if st.session_state.model_image_file:
        model_image_path = save_uploaded_file(st.session_state.model_image_file)
        model_image = Image.open(model_image_path)
        model_image = model_image.resize((IMAGE_DIMENSION, IMAGE_DIMENSION), Image.Resampling.LANCZOS)

    if st.session_state.garment_image_file:
        garment_image_path = save_uploaded_file(st.session_state.garment_image_file)
        garment_image = Image.open(garment_image_path)
        garment_image = garment_image.resize((IMAGE_DIMENSION, IMAGE_DIMENSION), Image.Resampling.LANCZOS)

    # Display images
    col1, col2 = st.columns([1, 1])
    with col1:
        if model_image:
            st.image(model_image, caption="Model Image", width=IMAGE_CONTAINER_WIDTH)
    with col2:
        if garment_image:
            st.image(garment_image, caption="Garment Image", width=IMAGE_CONTAINER_WIDTH)

    # Buttons
    if st.sidebar.button("Try On"):
        if not model_image_path or not garment_image_path:
            st.warning("Please select both images.")
        else:
            st.text("Processing...")
            output_image_path = try_on(model_image_path, garment_image_path)
            if output_image_path:
                output_image = Image.open(output_image_path)
                output_image = output_image.resize((IMAGE_DIMENSION, IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                st.session_state.output_image = output_image  # Save output image in session state

    if st.sidebar.button("Try Other"):
        # Reset session state for new images
        st.session_state.output_image = None
        st.session_state.model_image_file = None
        st.session_state.garment_image_file = None
        # Clear displayed images
        model_image = None
        garment_image = None
        # Reload the page to clear selections
        st.rerun()


    if st.sidebar.button("Reset"):
        # Reset session state for new images
        st.session_state.output_image = None
        st.session_state.model_image_file = None
        st.session_state.garment_image_file = None
        # Clear displayed images
        model_image = None
        garment_image = None
        # Reload the page to clear selections
        st.rerun()


    # Display output image
    if st.session_state.output_image:
        st.write("## Output Image")
        st.image(st.session_state.output_image, caption="Output Image", width=IMAGE_CONTAINER_WIDTH)

        # Save image button
        save_path = st.text_input("Save Image As (with .png extension):", "")
        if st.button("Save Image"):
            if save_path:
                save_image(st.session_state.output_image, save_path)