import streamlit as st
import openai # Now we just import the module

st.title("🤖 Goouq Chatbot")

# --- Configuration for openai==0.28.1 ---
try:
    # Set the API key
    openai.api_key = st.secrets["GOOUQ_API_KEY"]

    # Set the API base URL (Goouq's API endpoint)
    openai.api_base = "https://api.groq.com/openai/v1"

except KeyError:
    st.error("Error: GOOUQ_API_KEY not found in Streamlit secrets. Please add it.")
    st.stop() # Stop the app if API key is missing
except Exception as e:
    st.error(f"An unexpected error occurred during API configuration: {e}")
    st.stop()
# --- End Configuration ---


# Initialize chat history (if not already done)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # --- API Call using openai.ChatCompletion for 0.28.1 ---
        try:
            response = openai.ChatCompletion.create( # Use ChatCompletion for chat models
                model="llama3-8b-8192", # Replace with the actual model name Goouq expects
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Iterate through the stream to display response
            for chunk in response:
                full_response += chunk.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        except openai.error.AuthenticationError:
            st.error("Authentication failed. Please check your GOOUQ_API_KEY in Streamlit secrets.")
            full_response = "Authentication error. Please check your API key."
        except openai.error.APIError as e:
            st.error(f"Goouq API Error: {e}")
            full_response = f"Goouq API error: {e}"
        except Exception as e:
            st.error(f"An unexpected error occurred during API call: {e}")
            full_response = f"An unexpected error occurred: {e}"
        # --- End API Call ---

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})