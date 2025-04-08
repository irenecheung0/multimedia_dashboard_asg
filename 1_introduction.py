import streamlit as st

with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

st.title("COMP7503 Multimedia Technologies Project")

st.write("This is the introduction page.")

st.write("This is the introduction page.")

st.write("This is the introduction page.")