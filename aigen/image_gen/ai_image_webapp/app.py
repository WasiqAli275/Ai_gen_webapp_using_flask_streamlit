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
import streamlit as st
from PIL import Image
import io
from providers import try_provider

# ✅ PAGE CONFIG — sabse pehle aur sirf ek baar
st.set_page_config(page_title="AI Image Generator", layout="centered")


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
form = st.form(key="gen_form")
prompt_form = form.text_input("Enter your prompt", key="prompt_form", placeholder="Enter your prompt here...")
form.markdown('<button class="glow-btn" type="submit">✨ Generate Image</button>', unsafe_allow_html=True)
submitted = form.form_submit_button("", help="Generate an AI image from your prompt.")


if submitted and prompt_form:
    with st.spinner("Generating..."):
        try:
            img_bytes, provider = try_provider(prompt_form)
            st.success(f"Image generated via {provider}")
            st.image(Image.open(io.BytesIO(img_bytes)))
            st.download_button("Download Image", img_bytes, file_name="generated.png")
        except Exception as e:
            st.error(f"Failed: {e}")

# --- GITHUB LINK FOOTER ---
st.markdown("""
    <style>
    .footer-box {
        margin-top: 48px;
        padding: 24px 0 12px 0;
        background: linear-gradient(90deg, #e0c3fc 0%, #8ec5fc 100%);
        border-radius: 18px 18px 0 0;
        text-align: center;
        box-shadow: 0 -2px 16px 0 rgba(142,197,252,0.10);
        border-top: 2px solid #cfd9df;
    }
    .github-link {
        display: inline-block;
        margin-top: 8px;
        padding: 10px 28px;
        background: linear-gradient(90deg, #232526, #3a6073);
        color: #fff;
        font-size: 1.15em;
        font-weight: 600;
        border-radius: 32px;
        text-decoration: none;
        box-shadow: 0 2px 12px 0 rgba(58,123,213,0.10);
        transition: background 0.3s, box-shadow 0.3s, transform 0.2s;
        letter-spacing: 1px;
    }
    .github-link:hover {
        background: linear-gradient(90deg, #3a7bd5, #232526);
        color: #fff;
        box-shadow: 0 4px 24px 0 rgba(58,123,213,0.18);
        transform: scale(1.04);
        text-decoration: none;
    }
    .footer-info {
        color: #232526;
        font-size: 1.08em;
        margin-top: 10px;
        margin-bottom: 0;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    </style>
    <div class="footer-box">
        <div class="footer-info">
            <b>About this app:</b> This AI Image Generator webapp was created by <span style="color:#3a7bd5;font-weight:600;">prof.Wasiq</span> as a data scientist.<br>
            It uses multiple AI APIs for robust, creative image generation. <br>
            For source code, updates, and more projects, visit the GitHub profile below:
        </div>
        <a class="github-link" href="https://github.com/WasiqAli275" target="_blank">🌐 View Wasiq's GitHub</a>
    </div>
""", unsafe_allow_html=True)
