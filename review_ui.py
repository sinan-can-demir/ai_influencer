"""
Streamlit review UI for Juno's drafts.

Run with: streamlit run review_ui.py

Layout/session-state plumbing is scaffolded. The TODO blocks are where
this actually calls into the pipeline -- fill those in with the same
functions driver.py already uses.
"""

import streamlit as st

from pipeline.draft import generate_draft, should_generate_image
from pipeline.image import image_pipeline
from driver import get_bluesky_client, get_bluesky_account, login, post_draft
from pipeline.queue import enqueue_draft

st.set_page_config(page_title="Juno Review", page_icon="🌱")
st.title("Juno — Draft Review")

if "draft_text" not in st.session_state:
    st.session_state.draft_text = None
if "image_path" not in st.session_state:
    st.session_state.image_path = None
    st.session_state.image_alt = None
if "posted" not in st.session_state:
    st.session_state.posted = False

if st.button("Generate Draft"):

    st.session_state.draft_text = generate_draft()
    st.session_state.image_path = None
    st.session_state.image_alt = None
    st.session_state.posted = False
    if should_generate_image(st.session_state.draft_text):
        st.session_state.image_path, st.session_state.image_alt = image_pipeline(st.session_state.draft_text)

if st.session_state.draft_text is not None:
    st.session_state.draft_text = st.text_area("Draft", value=st.session_state.draft_text, height=150)

    if st.session_state.image_path:
        st.image(st.session_state.image_path)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Post"):
            print("Post approved: success")
            client = get_bluesky_client()
            handle, app_password = get_bluesky_account()
            login(client, handle, app_password)
            post_draft(client,
                       st.session_state.draft_text,
                       st.session_state.image_path,
                       st.session_state.image_alt)
            st.session_state.posted = True
            st.session_state.draft_text = None
            st.session_state.image_path = None
            st.session_state.image_alt = None

    with col2:
        if st.button("Reject / start over"):
            st.session_state.draft_text= None
            st.session_state.image_path= None
            st.session_state.image_alt = None
            st.session_state.posted = False

    with col3:
        if st.button("Approve for scheduled posting"):
            enqueue_draft(st.session_state.draft_text, st.session_state.image_path, st.session_state.image_alt)
            # reset 
            st.session_state.draft_text= None
            st.session_state.image_path= None
            st.session_state.image_alt = None
            st.session_state.posted = False

if st.session_state.posted:
    st.success("Posted!")
