import streamlit as st
import requests
import re
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="Football RAG Assistant", page_icon="⚽", layout="wide")

st.title("⚽ Tactical RAG Analytics")
st.markdown("Query the cloud-native vector database to visually retrieve semantic tactical events.")

query = st.text_input("Enter a tactical scenario (e.g., 'Mbappe passing'):")

if st.button("🔍 Search Tactical Database"):
    if query:
        with st.spinner("Searching Neon vector database..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/search", 
                    json={"prompt": query, "top_k": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    # Split UI into two columns for desktop viewing
                    col1, col2 = st.columns([1, 1.5])
                    
                    with col1:
                        st.subheader("📊 Top Semantic Matches")
                        for match in results:
                            st.info(f"**⏱️ {match['time']} | 🏃 {match['player']}** (Confidence: {match['confidence_score']})")
                            st.write(f"📝 {match['description']}")
                            st.divider()
                            
                    with col2:
                        st.subheader("📈 Tactical Pitch Map")
                        
                        # Initialize a metric pitch
                        pitch = Pitch(pitch_color='grass', line_color='white', stripe=True, pitch_length=105, pitch_width=68)
                        fig, ax = pitch.draw(figsize=(8, 6))
                        
                        # Extract coordinates and plot events
                        for idx, match in enumerate(results):
                            desc = match['description']
                            # Regex to capture "X:105.0m, Y:68.0m"
                            coords = re.findall(r'X:([0-9.]+)[a-zA-Z]*,\s*Y:([0-9.]+)[a-zA-Z]*', desc)
                            
                            if coords:
                                start_x, start_y = float(coords[0][0]), float(coords[0][1])
                                # Plot start location
                                pitch.scatter(start_x, start_y, ax=ax, c='red', edgecolors='black', s=150, zorder=2)
                                ax.text(start_x, start_y - 2, f"#{idx+1}", color="white", fontsize=10, ha="center")
                                
                                # Plot pass/shot trajectory if end coordinates exist
                                if len(coords) > 1:
                                    end_x, end_y = float(coords[1][0]), float(coords[1][1])
                                    pitch.arrows(start_x, start_y, end_x, end_y, width=2, headwidth=8, headlength=8, color='yellow', ax=ax, zorder=1)
                        
                        st.pyplot(fig)
                        
                else:
                    st.error(f"Backend Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Failed to connect to the backend. Ensure your FastAPI server is running!")