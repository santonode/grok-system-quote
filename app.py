# app.py
# This is a simple Streamlit web app for quote analysis using the xAI Grok API for searching and analyzing costs.
# To deploy on render.com:
# 1. Create a new Web Service on render.com, connect to your GitHub repo containing this file and requirements.txt.
# 2. Set the build command to: pip install -r requirements.txt
# 3. Set the start command to: streamlit run app.py --server.port $PORT --server.enableCORS false
# 4. Add an environment variable XAI_API_KEY with your API key obtained from https://x.ai/api
# Note: Using the Grok API may incur costs, especially for live search. See xAI docs for details.

import streamlit as st
import requests
import os

# Get API key from environment variable
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    st.error("XAI_API_KEY environment variable not set. Please set it with your xAI API key from https://x.ai/api")
    st.stop()

st.title("Quote Analysis Tool")

project_desc = st.text_area("Project Description", help="Describe the project, e.g., 'Kitchen remodel including new cabinets and countertops.'")
city = st.text_input("City", help="Enter the city in the United States.")
zip_code = st.text_input("Zip Code", help="Enter the zip code.")
quoted_cost = st.number_input("Quoted Cost ($)", min_value=0.0, help="Enter the cost from the quote.")

if st.button("Analyze Quote"):
    if not project_desc or not city or not zip_code or quoted_cost == 0.0:
        st.error("Please fill in all fields.")
    else:
        # Construct the prompt for Grok
        prompt = (
            f"Search the web for average or typical costs of similar projects to: '{project_desc}' "
            f"in or near {city}, {zip_code}, United States. "
            f"The quoted cost provided is ${quoted_cost:.2f}. "
            f"Compare the quoted cost to the costs you find, analyze if it seems high, low, or reasonable, "
            f"and explain your reasoning. Include sources for the costs you reference and format your output in asy to read font."
        )

        # API request setup
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "grok-4",  # Use the latest Grok model; check xAI docs for available models
            "messages": [{"role": "user", "content": prompt}],
            "search_parameters": {
                "mode": "on",
                "sources": [{"type": "web", "country": "US"}],
                "return_citations": True
            },
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            st.markdown("### Analysis")
            st.write(analysis)
            # If citations are available (depending on API response), they might be in result['usage'] or elsewhere; check docs
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling xAI API: {e}")
        except KeyError:
            st.error("Unexpected API response format. Check xAI API documentation for changes.")


