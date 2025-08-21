# app.py
# Streamlit web app for quote analysis using the xAI Grok API.
# Deploy on render.com with:
# Build: pip install -r requirements.txt
# Start: streamlit run app.py --server.port $PORT --server.enableCORS false
# Env: XAI_API_KEY from https://x.ai/api

import streamlit as st
import requests
import os
import json

# Get API key
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    st.error("XAI_API_KEY not set. Get it from https://x.ai/api")
    st.stop()

st.title("Quote Analysis Tool")

project_desc = st.text_area("Project Description", help="Describe the project (max 500 chars).")
if len(project_desc) > 500:
    st.error("Project description exceeds 500 characters. Please shorten it.")
    st.stop()
city = st.text_input("City", help="Enter the city in the US.")
zip_code = st.text_input("Zip Code", help="Enter the zip code.")
quoted_cost = st.number_input("Quoted Cost ($)", min_value=0.0, help="Enter the quoted cost.")

if st.button("Analyze Quote"):
    if not project_desc or not city or not zip_code or quoted_cost == 0.0:
        st.error("Please fill in all fields.")
    else:
        # Construct concise prompt
        prompt = (
            f"Search the web for average costs of '{project_desc}' in or near {city}, {zip_code}, US. "
            f"Quoted cost: ${quoted_cost:.2f}. Compare and state if it’s high, low, or reasonable. "
            f"Explain briefly, include up to 3 sources, and keep response concise."
        )

        # API request setup
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "grok-4",
            "messages": [{"role": "user", "content": prompt}],
            "search_parameters": {
                "mode": "on",
                "sources": [{"type": "web", "country": "US"}],
                "return_citations": True
            },
            "temperature": 0.7,
            "max_tokens": 4096  # Increased to prevent truncation
        }

        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            # Check for truncation
            if result["choices"][0].get("finish_reason") == "length":
                st.warning("Response may be incomplete due to token limit. Try simplifying the description.")
            # Log response for debugging
            with open("api_response.json", "w") as f:
                json.dump(result, f, indent=2)
            st.markdown("### Analysis")
            with st.expander("View Detailed Analysis"):
                st.write(analysis)
            with st.expander("Debug: Raw API Response"):
                st.json(result)
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling xAI API: {e}")
        except KeyError:
            st.error("Unexpected API response format. Check xAI API docs.")
