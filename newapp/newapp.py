### this is my second practice webapp i can add an image, video and voice in this webapp and deploy it in streamlit to sharing my friends

# # import libraries
import streamlit as st
from PIL import Image
# st.write("""
#          # add media file in streamlit Web App
#          """)
# # add image
# st.write("""
#          ## Image 🐆
#          """)
# image1 = Image.open('snowleapardimage.jpg')
# st.write(image1)
# # add video
# st.write("""
#          ## Video 🎥
#          """)
# video1 = open("video.mp4", "rb")
# st.video(video1)
# # add audio
# st.write("""
#          ## Audio🔊
#          """)
# audio1 = open("voice_snowleapord.mp3", "rb")
# st.audio(audio1)

if st.checkbox('show code'):
    with st.echo():
        # import libraries
        import streamlit as st
        from PIL import Image
        st.write("""
                 # add media file in streamlit Web App
                """)
        # add image
        st.write("""
                 ## Image 🐆
                """)
        image1 = Image.open('snowleapardimage.jpg')
        st.write(image1)
        # add video
        st.write("""
                 ## Video 🎥
                 """)
        video1 = open("video.mp4", "rb")
        st.video(video1)
        # add audio
        st.write("""
                 ## Audio🔊
                """)
        audio1 = open("voice_snowleapord.mp3", "rb")
        st.audio(audio1)
