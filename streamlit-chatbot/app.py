import streamlit as st
import openai
import uuid
import random

# --- Configuration for Groq API ---
try:
    openai.api_key = st.secrets["GROQ_API_KEY"]
    openai.api_base = "https://api.groq.com/openai/v1"
except KeyError:
    st.error("Error: GROQ_API_KEY not found in Streamlit secrets. Please add your Groq API key.")
    st.stop()

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="🫒live", layout="centered")

# --- Initialize Session State Variables ---
if "messages" not in st.session_state:
    st.session_state["messages"] = {} # messages will be per-mode if needed
if "current_chat_messages" not in st.session_state: # Specific for general chat mode
    st.session_state["current_chat_messages"] = []
if "user_avatar" not in st.session_state:
    st.session_state["user_avatar"] = "😀" # Default emoji for the user
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "Home" # Default mode: Home (avatar selection)
if "study_topic" not in st.session_state:
    st.session_state["study_topic"] = "None"
if "study_messages" not in st.session_state: # Messages for study mode
    st.session_state["study_messages"] = {} # e.g., {"Science": [], "Maths": []}

# --- Custom CSS for Olive Theme and Layout ---
st.markdown(
    """
    <style>
    /* Olive Color Palette */
    :root {
        --olive-dark: #3a503e;   /* Darker olive for accents/text */
        --olive-medium: #55725c; /* Medium olive for primary elements */
        --olive-light: #8da18b;  /* Lighter olive for backgrounds */
        --olive-accent: #a3b899; /* Even lighter, more muted green */
        --cream-white: #f5f5dc;  /* Creamy white for main content background */
        --text-dark: #333333;    /* Dark grey for general text */
        --text-light: #ffffff;   /* White for text on dark backgrounds */
        --olive-background: #8da18b; /* Explicitly set for main page background */
    }

    /* Overall App Background */
    .stApp {
        background-color: var(--olive-background); /* Changed to olive green */
        color: var(--text-dark); /* Default text color for main content */
    }

    /* Sidebar Styling */
    .st-emotion-cache-1jmve0f { /* Targeting the sidebar container */
        background-color: var(--olive-medium);
        border-right: 1px solid var(--olive-dark);
        color: var(--text-light); /* Text within sidebar is white */
    }
    .st-emotion-cache-1jmve0f .st-emotion-cache-16txt4v { /* Sidebar header/title */
        color: var(--text-light);
    }
    .st-emotion-cache-1jmve0f .st-emotion-cache-v01mih { /* Sidebar radio button labels */
        color: var(--text-light) !important;
    }
    .st-emotion-cache-1jmve0f .st-emotion-cache-199z13k { /* Active radio button in sidebar */
        background-color: var(--olive-dark) !important;
        border-radius: 5px;
    }
    .st-emotion-cache-1jmve0f .st-emotion-cache-v01mih p { /* Text within sidebar */
        color: var(--text-light);
    }

    /* Main Content Styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--olive-dark);
    }
    .stButton>button {
        background-color: var(--olive-medium);
        color: var(--text-light);
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: var(--olive-dark);
        color: var(--text-light);
    }
    .stTextInput>div>div>input {
        border-color: var(--olive-medium);
        color: var(--text-dark); /* Ensure text input color is dark */
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--olive-dark);
        box-shadow: 0 0 0 0.2rem rgba(85, 114, 92, 0.25); /* Medium olive with transparency */
    }

    /* Fix for radio button labels in main content area */
    .st-emotion-cache-v01mih p { /* This targets all paragraph text in Streamlit components */
        color: var(--text-dark); /* Make text dark for visibility on light backgrounds */
    }
    /* Specific targeting for radio button labels if needed for more precision */
    .st-emotion-cache-199z13k + div p { /* This targets the text next to radio buttons/checkboxes */
        color: var(--text-dark) !important;
    }


    /* Chat Messages - User */
    .stChatMessage.st-emotion-cache-1c7y2c1.user { /* Targeting user message container */
        background-color: var(--olive-accent); /* Lighter olive background */
        color: var(--text-dark);
        border-radius: 15px 15px 5px 15px; /* Rounded corners, less rounded at bottom-right */
        padding: 15px;
        margin-bottom: 10px;
    }
    .stChatMessage.st-emotion-cache-1c7y2c1.user .st-emotion-cache-zt5igk { /* User message text */
        color: var(--text-dark);
    }

    /* Chat Messages - Assistant */
    .stChatMessage.st-emotion-cache-1c7y2c1.assistant { /* Targeting assistant message container */
        background-color: var(--olive-light); /* Slightly lighter olive background */
        color: var(--text-dark);
        border-radius: 15px 15px 15px 5px; /* Rounded corners, less rounded at bottom-left */
        padding: 15px;
        margin-bottom: 10px;
    }
    .stChatMessage.st-emotion-cache-1c7y2c1.assistant .st-emotion-cache-zt5igk { /* Assistant message text */
        color: var(--text-dark);
    }


    /* Avatar Selection Screen CSS */
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 80vh; /* Take up most of the viewport height */
        padding: 20px;
        background-color: var(--olive-background); /* Ensure consistency for this container */
    }
    .avatar-display {
        font-size: 150px; /* Large emoji size */
        margin-bottom: 20px;
    }
    .emoji-button-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 20px;
        max-width: 600px; /* Limit width of emoji grid */
    }
    .emoji-button {
        background-color: var(--cream-white);
        border: 1px solid var(--olive-accent);
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 30px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        color: var(--text-dark);
    }
    .emoji-button:hover {
        background-color: var(--olive-accent);
        border-color: var(--olive-dark);
    }
    /* Hide the default Streamlit header/footer for a cleaner initial look */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .st-emotion-cache-z5fcl4 { padding-top: 2rem; } /* Adjust top padding if header is hidden */
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar for Navigation ---
with st.sidebar:
    st.title("🫒live Bot")
    st.markdown("---") # Separator

    # Current Avatar Display (only visible when a mode is active)
    if st.session_state["app_mode"] != "Home":
        st.subheader("Your Buddy:)")
        st.markdown(f'<div style="font-size: 50px; text-align: center;">{st.session_state["user_avatar"]}</div>', unsafe_allow_html=True)
        if st.button("Change Friend", key="change_avatar_sidebar"):
            st.session_state["app_mode"] = "Home"
            st.session_state["current_chat_messages"] = [] # Clear chat history if changing avatar
            st.session_state["study_messages"] = {} # Clear study messages too
            st.rerun()
        st.markdown("---")


    # Main Navigation
    st.subheader("What do you want to do?")
    app_mode = st.radio(
        "Choose a section:",
        ("Chat with Bot", "Study Time", "Game Corner"),
        key="app_mode_radio"
    )
    # Update app_mode in session state (if not "Home")
    if app_mode == "Chat with Bot":
        st.session_state["app_mode"] = "Chat"
    elif app_mode == "Study Time":
        st.session_state["app_mode"] = "Study"
    elif app_mode == "Game Corner":
        st.session_state["app_mode"] = "Games"


# --- Home Screen (Avatar Selection) ---
if st.session_state["app_mode"] == "Home":
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    st.title("Choose Your Chat Friend!")

    # Display current selected emoji (large)
    st.markdown(f'<div class="avatar-display">{st.session_state["user_avatar"]}</div>', unsafe_allow_html=True)

    # Text input for custom emoji (optional)
    custom_emoji = st.text_input(
        "Or type your own emoji below:",
        value=st.session_state["user_avatar"],
        max_chars=2, # Restrict to typically 1-2 characters for an emoji
        help="Paste any emoji here!"
    )
    if custom_emoji and custom_emoji != st.session_state["user_avatar"]:
        st.session_state["user_avatar"] = custom_emoji
        st.rerun() # Rerun to update the displayed large emoji

    st.markdown("### Or pick from these:")

    # Grid of common emojis as buttons
    common_emojis = ["😀", "😊", "🥳", "😎", "👾", "🤖", "🚀", "😺", "🐶", "🦉", "🦁", "🦄", "🌈", "☀️", "🌟", "💡", "🍔", "🍕", "🎈", "📚", "🧪", "📐", "🗺️", "🗣️"]
    
    cols = st.columns(6) # Adjust number of columns as needed
    for i, emoji in enumerate(common_emojis):
        with cols[i % 6]:
            if st.button(emoji, key=f"emoji_btn_{emoji}", use_container_width=True):
                st.session_state["user_avatar"] = emoji
                st.rerun() # Rerun to update the displayed large emoji

    st.markdown("</div>", unsafe_allow_html=True) # Close centered-container

    st.markdown("---") # Separator before the button
    if st.button("Start Chat!", type="primary", use_container_width=True, key="start_chat_btn"):
        st.session_state["avatar_chosen"] = True
        st.session_state["app_mode"] = "Chat" # Automatically switch to Chat mode after choosing avatar
        st.rerun() # Rerun to switch to chat mode

# --- Chat with Bot Section ---
elif st.session_state["app_mode"] == "Chat":
    st.title("Let's Chat!")

    # Display chat messages for this mode
    for message in st.session_state["current_chat_messages"]:
        avatar = "🫒" if message["role"] == "assistant" else st.session_state["user_avatar"]
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Chat Input and Logic for general chat
    if prompt := st.chat_input("What do you want to talk about?"):
        st.session_state["current_chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=st.session_state["user_avatar"]):
            st.markdown(prompt)

        messages_for_api = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state["current_chat_messages"]
        ]

        with st.chat_message("assistant", avatar="🫒"):
            stream = openai.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages_for_api,
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state["current_chat_messages"].append({"role": "assistant", "content": response})

# --- Study Time Section ---
elif st.session_state["app_mode"] == "Study":
    st.title("📚 Study Time!")
    st.markdown("---")

    # Select Study Topic
    st.subheader("What do you want to learn today?")
    # The `p` within `st-emotion-cache-v01mih` is the target for text color
    # This change specifically sets the text color for these radio buttons
    # in the main content area to be dark, ensuring visibility.
    study_topic = st.radio(
        "Choose a subject:",
        ("Science", "Maths", "Social Studies", "Language"),
        key="study_topic_radio"
    )
    st.session_state["study_topic"] = study_topic # Store chosen topic

    # Initialize messages for the specific study topic
    if study_topic not in st.session_state["study_messages"]:
        st.session_state["study_messages"][study_topic] = []
        # Add an initial greeting from the tutor
        initial_greeting = f"Hello! I'm your friendly {study_topic} tutor. What would you like to learn about today in {study_topic}?"
        st.session_state["study_messages"][study_topic].append({"role": "assistant", "content": initial_greeting})

    # Display chat messages for the current study topic
    for message in st.session_state["study_messages"][study_topic]:
        avatar = "🫒" if message["role"] == "assistant" else st.session_state["user_avatar"]
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Study Chat Input and Logic
    if prompt := st.chat_input(f"Ask me about {study_topic}..."):
        st.session_state["study_messages"][study_topic].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=st.session_state["user_avatar"]):
            st.markdown(prompt)

        # Build messages for API with a system prompt for the tutor
        system_prompt = f"You are a kind, patient, and knowledgeable tutor for kids learning about {study_topic}. Explain concepts clearly, use simple language, and provide examples. Keep responses concise and engaging for a young audience. If the question is not about {study_topic}, gently guide them back."
        
        messages_for_api = [{"role": "system", "content": system_prompt}] + \
                           [{"role": m["role"], "content": m["content"]} for m in st.session_state["study_messages"][study_topic]]

        with st.chat_message("assistant", avatar="🫒"):
            stream = openai.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages_for_api,
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state["study_messages"][study_topic].append({"role": "assistant", "content": response})


# --- Game Corner Section ---
elif st.session_state["app_mode"] == "Games":
    st.title("🎮 Game Corner!")
    st.markdown("---")
    st.subheader("Welcome to the Game Corner!")
    st.markdown("This is where we'll add fun games to play.")
    st.markdown("---")

    st.write("Games are coming soon! We could have:")
    st.markdown("- **One Player vs Bot:** Like a simple 'Guess the Number' or 'Rock-Paper-Scissors' with the computer.")
    st.markdown("- **Two Player Games:** Where two friends can play together on the same screen (e.g., Tic-Tac-Toe).")

    st.markdown("Stay tuned! If you have ideas for a game, let me know in the chat!")