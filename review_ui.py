"""
Streamlit review UI for Juno's drafts.

Run with: streamlit run review_ui.py

Layout/session-state plumbing is scaffolded. The TODO blocks are where
this actually calls into the pipeline -- fill those in with the same
functions driver.py already uses.
"""

import streamlit as st

from pipeline.draft import generate_draft
from pipeline.image import image_pipeline
from driver import get_bluesky_client, get_bluesky_account, login, post_draft

st.set_page_config(page_title="Juno Review", page_icon="🌱")
st.title("Juno — Draft Review")

if "draft_text" not in st.session_state:
    st.session_state.draft_text = None
if "image_path" not in st.session_state:
    st.session_state.image_path = None
if "posted" not in st.session_state:
    st.session_state.posted = False

if st.button("Generate Draft"):

    st.session_state.draft_text = generate_draft()
    st.session_state.image_path = None
    st.session_state.posted = False

if st.session_state.draft_text is not None:
    st.text_area("Draft", key="draft_text", height=150)

    include_image = st.checkbox("Include an image")
    if include_image and st.session_state.image_path is None:
        if st.button("Generate Image"):
            st.session_state.image_path = image_pipeline(st.session_state.draft_text)

    if st.session_state.image_path:
        st.image(st.session_state.image_path)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Post"):
            print("Post approved: success")
            client = get_bluesky_client()
            handle, app_password = get_bluesky_account()
            login(client, handle, app_password)
            post_draft(client, 
                       st.session_state.draft_text, 
                       st.session_state.image_path)
            st.session_state.posted = True

    with col2:
        if st.button("Reject / start over"):
            st.session_state.draft_text= None
            st.session_state.image_path= None
            st.session_state.posted = False

if st.session_state.posted:
    st.success("Posted!")
