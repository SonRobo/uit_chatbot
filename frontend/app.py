import streamlit as st
import requests
import uuid

API_URL = "http://192.168.43.86:8080/chat/chatDomain"  # Your actual backend endpoint

# Generate new room_id on load or after clear
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())

# Clear button — creates new room
if st.sidebar.button("Clear Conversation"):
    st.session_state.room_id = str(uuid.uuid4())
    st.rerun()

# Display current room ID
st.sidebar.markdown(f"**Room ID:** `{st.session_state.room_id}`")

# Input box
if prompt := st.chat_input("Ask something..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("agent"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        payload = {
            "room_id": st.session_state.room_id,
            "query": prompt
        }

        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 200:
                response = res.json().get("response", "No response.")
            else:
                response = f"Error {res.status_code}: {res.text}"
        except Exception as e:
            response = f"Request failed: {e}"

        placeholder.markdown(response)
