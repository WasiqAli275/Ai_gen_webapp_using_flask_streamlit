# import streamlit as st
# from PIL import Image
# import io 
# from providers import try_provider

# st.set_page_config(page_title="AI Image Generator", layout="centered") 
# st.title("🖼️ AI Image Generator webapp")




# prompt = st.text_input("Enter your prompt") 
# if st.button("Generate Image") and prompt:
#     with st.spinner("Generating..."):
#         try: 
#             img_bytes, provider = try_provider(prompt) 
#             st.success(f"Image generated via {provider}") 
#             st.image(Image.open(io.BytesIO(img_bytes))) 
#             st.download_button("Download Image", img_bytes, file_name="generated.png") 
#         except Exception as e: 
#             st.error(f"Failed: {e}")
            
            
# st.set_page_config(page_title="Gradient Header Demo", layout="wide")

# st.markdown("""
#     <style>
#     .custom-header {
#         background: linear-gradient(to right, #ff512f, #dd2476);
#         padding: 20px;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         font-size: 30px;
#         font-weight: bold;
#         margin-bottom: 20px;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.markdown('<div class="custom-header">🔥 AI WebApp - Powered by 3 APIs</div>', unsafe_allow_html=True)

# st.write("👇 Start your generation task here...")




import streamlit as st
from PIL import Image
import io
from providers import try_provider
import fitz  # PyMuPDF
import tempfile
import os
from io import BytesIO


# ✅ PAGE CONFIG — sabse pehle aur sirf ek baar
st.set_page_config(page_title="AI Image Generator", layout="centered")



# --- SIDEBAR: IMAGE SETTINGS ---
st.sidebar.title("Image Settings")
width = st.sidebar.number_input("Width", 256, 4096, 1024, key="width")
height = st.sidebar.number_input("Height", 256, 4096, 1024, key="height")
resolution = st.sidebar.selectbox("Resolution", ["HD", "Full HD", "2K", "4K"], key="resolution")


# --- SIDEBAR: FILE TOOLS ---
st.sidebar.markdown("---")
st.sidebar.title("File Tools")
st.sidebar.info("""
**File Tools** allow you to:
- Convert PDF to images (multi-page supported)
- Merge images into a single PDF
- Change image formats (JPG ↔ PNG)

Just upload your files and select the conversion type in the File Converter tab below!
""")

# --- MAIN TABS ---
tab1, tab2 = st.tabs(["Image Generator", "File Converter"])

# --- SESSION STATE MANAGEMENT ---
if "converted_files" not in st.session_state:
    st.session_state["converted_files"] = []
if "last_conversion" not in st.session_state:
    st.session_state["last_conversion"] = None

# --- CACHING FOR FILE PROCESSING ---
@st.cache_data(show_spinner=False)
def convert_pdf_to_images(pdf_bytes, out_format="png"):
    images = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                pix = page.get_pixmap()
                img_bytes = BytesIO()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(img_bytes, format=out_format.upper())
                images.append(img_bytes.getvalue())
        return images, None
    except Exception as e:
        return None, str(e)

@st.cache_data(show_spinner=False)
def convert_images_to_pdf(image_files):
    try:
        images = [Image.open(BytesIO(f.read() if hasattr(f, 'read') else f)) for f in image_files]
        img_converted = [img.convert("RGB") for img in images]
        pdf_bytes = BytesIO()
        img_converted[0].save(pdf_bytes, format="PDF", save_all=True, append_images=img_converted[1:])
        return pdf_bytes.getvalue(), None
    except Exception as e:
        return None, str(e)

@st.cache_data(show_spinner=False)
def convert_image_format(image_bytes, out_format="png"):
    try:
        img = Image.open(BytesIO(image_bytes))
        out_bytes = BytesIO()
        img.save(out_bytes, format=out_format.upper())
        return out_bytes.getvalue(), None
    except Exception as e:
        return None, str(e)

# --- MAIN TAB 1: IMAGE GENERATOR ---
with tab1:
    # ✅ CUSTOM CSS for gradient header and text
    st.markdown("""
        <style>
        .custom-header {
            background: linear-gradient(90deg, #f8ffae, #a6ffcb, #e0c3fc, #f9f9f9, #cfd9df);
            padding: 24px;
            border-radius: 16px;
            color: #333;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 32px;
            letter-spacing: 2px;
            box-shadow: 0 4px 24px 0 rgba(200,200,200,0.10);
            border: 2px solid #fff6;
        }
        .gradient-text {
            background: linear-gradient(90deg, #3a7bd5, #3a6073, #283e51, #232526, #000000);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 18px;
            text-align: center;
            letter-spacing: 1.5px;
        }
        .subtle-box {
            background: linear-gradient(90deg, #f8ffae 0%, #43c6ac 100%);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 18px;
            color: #222;
            font-size: 18px;
            font-weight: 500;
            box-shadow: 0 2px 12px 0 rgba(67,198,172,0.10);
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ GRADIENT HEADER
    st.markdown('<div class="custom-header">🔥 <span class="gradient-text">AI Image Generator webapp</span> <br> <span style="font-size:18px;font-weight:400; color:#333;">Powered by <span class="gradient-text">prof.Wasiq</span> as a data scientist</span></div>', unsafe_allow_html=True)

    # ✅ Subtle info box
    st.markdown('<div class="subtle-box">Enter a creative prompt below and generate stunning AI images instantly!<br>Try prompts like <b>"A futuristic city at sunset"</b> or <b>"A cat astronaut in watercolor style"</b>.</div>', unsafe_allow_html=True)

    # ✅ Custom glowing button using HTML/CSS
    st.markdown("""
        <style>
        .glow-btn {
            display: inline-block;
            padding: 0.75em 2.5em;
            font-size: 1.2em;
            font-weight: bold;
            color: #fff;
            background: linear-gradient(90deg, #ff512f, #dd2476, #1fa2ff, #12d8fa, #a6ffcb);
            border: none;
            border-radius: 32px;
            box-shadow: 0 0 16px 4px #1fa2ff80, 0 0 32px 8px #ff512f40;
            cursor: pointer;
            transition: box-shadow 0.3s, transform 0.2s;
            margin-bottom: 18px;
            margin-top: 8px;
            outline: none;
            letter-spacing: 1px;
            position: relative;
            z-index: 2;
        }
        .glow-btn:hover, .glow-btn:focus {
            box-shadow: 0 0 32px 8px #1fa2ffcc, 0 0 64px 16px #ff512fcc;
            transform: scale(1.04);
        }
        </style>
    """, unsafe_allow_html=True)

    # Use a form to capture prompt and button click with custom HTML
    form = st.form(key="gen_form_tab1")
    prompt_form = form.text_input("Enter your prompt", key="prompt_form_tab1", placeholder="Enter your prompt here...")
    form.markdown('<button class="glow-btn" type="submit">✨ Generate Image</button>', unsafe_allow_html=True)
    submitted = form.form_submit_button("", help="Generate an AI image from your prompt.")

    if submitted and prompt_form:
        # Prepend resolution/size to prompt
        prompt_full = f"Create image at {width}x{height} {resolution} resolution. {prompt_form}"
        with st.spinner("Generating..."):
            try:
                img_bytes, provider = try_provider(prompt_full)
                st.success(f"Image generated via {provider}")
                st.image(Image.open(io.BytesIO(img_bytes)))
                st.download_button("Download Image", img_bytes, file_name="generated.png")
            except Exception as e:
                st.error(f"Failed: {e}")

# --- MAIN TAB 2: FILE CONVERTER ---
with tab2:
    st.header("File Converter")
    uploaded_files = st.file_uploader("Upload File(s)", type=["jpg","jpeg","png","pdf"], accept_multiple_files=True, key="file_uploader")
    convert_option = st.radio("Convert:", ["PDF to Image", "Image to PDF", "Image Format Change"], key="convert_option")

    # Dynamic format options
    out_format = None
    if convert_option == "PDF to Image":
        out_format = st.selectbox("Output Image Format", ["png", "jpg"], key="pdf2img_format")
    elif convert_option == "Image to PDF":
        st.info("All uploaded images will be merged into a single PDF.")
    elif convert_option == "Image Format Change":
        out_format = st.selectbox("Convert Images To", ["png", "jpg"], key="img2img_format")

    convert_btn = st.button("Convert", key="convert_btn")

    if convert_btn:
        with st.spinner("Converting..."):
            try:
                if not uploaded_files:
                    st.error("Please upload at least one file.")
                elif convert_option == "PDF to Image":
                    for file in uploaded_files:
                        if file.type != "application/pdf":
                            st.warning(f"{file.name} is not a PDF. Skipped.")
                            continue
                        images, err = convert_pdf_to_images(file.read(), out_format)
                        if err:
                            st.error(f"{file.name}: {err}")
                        else:
                            for idx, img_bytes in enumerate(images):
                                fname = f"{os.path.splitext(file.name)[0]}_page{idx+1}.{out_format}"
                                st.image(img_bytes, caption=fname)
                                st.download_button(f"Download {fname}", img_bytes, file_name=fname)
                elif convert_option == "Image to PDF":
                    # Only allow images
                    image_files = [f for f in uploaded_files if f.type in ["image/jpeg", "image/png"]]
                    if not image_files:
                        st.error("Please upload at least one image file.")
                    else:
                        pdf_bytes, err = convert_images_to_pdf(image_files)
                        if err:
                            st.error(f"Conversion failed: {err}")
                        else:
                            st.success("PDF created!")
                            st.download_button("Download PDF", pdf_bytes, file_name="merged.pdf")
                elif convert_option == "Image Format Change":
                    for file in uploaded_files:
                        if file.type not in ["image/jpeg", "image/png"]:
                            st.warning(f"{file.name} is not an image. Skipped.")
                            continue
                        img_bytes, err = convert_image_format(file.read(), out_format)
                        if err:
                            st.error(f"{file.name}: {err}")
                        else:
                            fname = f"{os.path.splitext(file.name)[0]}.{out_format}"
                            st.image(img_bytes, caption=fname)
                            st.download_button(f"Download {fname}", img_bytes, file_name=fname)
            except Exception as e:
                st.error(f"Conversion failed: {e}")





# --- BEAUTIFUL CUSTOM FOOTER SECTION ---
footer = st.container()
footer.markdown("""
    <style>
    .footer-main {
        background: linear-gradient(90deg, #e0c3fc 0%, #8ec5fc 100%);
        border-radius: 24px 24px 0 0;
        margin-top: 48px;
        padding: 32px 0 16px 0;
        box-shadow: 0 -2px 24px 0 rgba(142,197,252,0.13);
        border-top: 2px solid #cfd9df;
        width: 100%;
    }
    .footer-cols {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        gap: 32px;
        max-width: 1100px;
        margin: 0 auto;
    }
    .footer-col {
        flex: 1 1 250px;
        min-width: 220px;
        border-radius: 18px;
        padding: 24px 18px 18px 18px;
        box-shadow: 0 2px 12px 0 rgba(58,123,213,0.08);
        margin-bottom: 12px;
    }
    /* Custom gradients for each section */
    .footer-col:nth-child(1) {
        background: linear-gradient(135deg, #f8ffae 0%, #43c6ac 100%);
    }
    .footer-col:nth-child(2) {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    }
    .footer-col:nth-child(3) {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .footer-title {
        font-size: 1.3em;
        font-weight: 700;
        color: #3a7bd5;
        margin-bottom: 12px;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px #e0c3fc80;
    }
    .footer-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-list li {
        margin-bottom: 8px;
        font-size: 1.08em;
        color: #232526;
        transition: color 0.2s;
    }
    .footer-list li a {
        color: #232526;
        text-decoration: none;
        transition: color 0.2s;
        font-weight: 500;
    }
    .footer-list li a:hover {
        color: #3a7bd5;
        text-decoration: underline;
    }
    .footer-contact {
        font-size: 1.08em;
        color: #232526;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .footer-contact a {
        color: #3a7bd5;
        text-decoration: none;
        font-weight: 600;
    }
    .footer-contact a:hover {
        text-decoration: underline;
        color: #232526;
    }
    .footer-copyright {
        text-align: center;
        color: #232526;
        font-size: 1em;
        margin-top: 18px;
        opacity: 0.7;
    }
    </style>
    <div class="footer-main">
      <div class="footer-cols">
        <div class="footer-col">
          <div class="footer-title">About</div>
          <ul class="footer-list">
            <li><a href="#">Home</a></li>
            <li><a href="#">Services</a></li>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">About Us</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <div class="footer-title">Legal</div>
          <ul class="footer-list">
            <li><a href="https://example.com/terms" target="_blank">Terms of Service</a></li>
            <li><a href="https://example.com/privacy" target="_blank">Privacy Policy</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <div class="footer-title">Contact</div>
          <div class="footer-contact">Email: <a href="mailto:wasiq5772@gmail.com">wasiq5772@gmail.com</a></div>
          <div class="footer-contact">GitHub: <a href="https://github.com/wasiqali275" target="_blank">Your Profile</a></div>
          <div class="footer-contact">Upwork: <a href="https://www.upwork.com/freelancers/~016348ec60528b2fd9" target="_blank">link</a></div>
        </div>
      </div>
      <div class="footer-copyright">
        &copy; 2025 prof.Wasiq | All rights reserved.
      </div>
    </div>
    """, unsafe_allow_html=True)
