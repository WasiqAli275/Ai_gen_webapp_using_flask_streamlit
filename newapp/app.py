# this is my testing webapp by using streamlit and github
import streamlit as st
from streamlit_embadcode import github_gist

link = "https://gist.github.com/WasiqAli275/3948ebd9105f074e71f77d7c14bb6cab"

st.write("embad github code:")

github_gist(link)
