import streamlit as st
import openai 

# Debug: Verify secrets load
st.title("🤖 Goouq Chatbot")
st.write("Secrets loaded:", list(st.secrets.keys()))

# Initialize client
try:
    client = openai.OpenAI( # Now, access OpenAI as an attribute of the imported openai module
    api_key=st.secrets["GOOUQ_API_KEY"],
    base_url="https://api.goouq.com/v1"
)
except KeyError:
    st.error("Missing GOOUQ_API_KEY in secrets.toml!")
    st.stop()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get Goouq response
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="goouq-model-name",  # Replace with actual model name
                messages=st.session_state.messages,
                stream=True
            )
            
            full_response = ""
            message_placeholder = st.empty()
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")