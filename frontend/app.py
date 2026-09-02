import streamlit as st
import requests

st.set_page_config(page_title="Football RAG Assistant", page_icon="⚽", layout="centered")

st.title("⚽ Tactical RAG Analytics")
st.markdown("Query the cloud-native vector database to instantly retrieve semantic tactical events.")

query = st.text_input("Enter a tactical scenario (e.g., 'Di Maria attacking'):")

if st.button("🔍 Search Tactical Database"):
    if query:
        with st.spinner("Searching Neon vector database..."):
            try:
                # Call your running FastAPI backend
                response = requests.post(
                    "http://127.0.0.1:8000/search", 
                    json={"prompt": query, "top_k": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("📊 Top Semantic Matches")
                    
                    for idx, match in enumerate(data.get("results", [])):
                        with st.container():
                            st.info(f"**⏱️ {match['time']} | 🏃 {match['player']}** (Confidence: {match['confidence_score']})")
                            st.write(f"📝 {match['description']}")
                            st.divider()
                else:
                    st.error(f"Backend Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Failed to connect to the backend. Ensure your FastAPI server is running in another terminal!")