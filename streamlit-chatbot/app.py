import streamlit as st
from groq import Groq
import uuid # For generating unique IDs for subjects/chats
import random
import json # For handling JSON string conversion for Firestore arrays/objects

# --- Firebase Imports (for Firestore) ---
# Ensure these are correctly imported for Streamlit Cloud deployment
from firebase_admin import credentials, initialize_app
from firebase_admin import auth as firebase_auth
from firebase_admin import firestore as firebase_firestore

# --- Firebase Initialization ---
# Check if Firebase app is already initialized to prevent multiple initializations
if not firebase_admin._apps:
    try:
        # Use Streamlit secrets for Firebase configuration
        # Ensure __firebase_config and __app_id are set in Streamlit Cloud secrets
        firebase_config = json.loads(st.secrets["__firebase_config"])
        cred = credentials.Certificate(firebase_config)
        initialize_app(cred, {'projectId': firebase_config['project_id']})
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.stop()

db = firebase_firestore.client()
# Get the app ID for document paths
APP_ID = st.secrets.get("__app_id", "default-app-id")

# --- Groq API Client Initialization ---
try:
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"],
    )
except KeyError:
    st.error("Error: GROQ_API_KEY not found in Streamlit secrets. Please add your Groq API key.")
    st.stop()

# --- Streamlit Page Configuration ---
# Use 'wide' layout for more space and expand the sidebar by default
st.set_page_config(page_title="🫒live Chatbot - Learning Companion", layout="wide", initial_sidebar_state="expanded")

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
        background-color: var(--olive-background);
        color: var(--text-dark);
    }

    /* Sidebar Styling - Making it fixed and prominent */
    .st-emotion-cache-1jmve0f { /* Targeting the sidebar container */
        background-color: var(--olive-medium);
        border-right: 1px solid var(--olive-dark);
        color: var(--text-light);
        width: 300px !important; /* Fixed width for sidebar */
        min-width: 300px !important;
        max-width: 300px !important;
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
    /* Hide the sidebar expander button as sidebar is always expanded */
    [data-testid="stSidebarExpander"] {
        display: none !important;
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

# --- Firebase Auth & Data Setup ---
# Use a global variable for user ID, initialized once authentication is ready
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "firebase_ready" not in st.session_state:
    st.session_state.firebase_ready = False

@st.cache_resource
def get_firestore_collections():
    """Returns Firestore collection references."""
    # Collections for user-specific data
    user_data_path = f"artifacts/{APP_ID}/users/{st.session_state.current_user_id}"
    return {
        "subjects": db.collection(f"{user_data_path}/subjects"),
        "chat_histories": db.collection(f"{user_data_path}/chat_histories"),
        "learning_progress": db.collection(f"{user_data_path}/learning_progress"),
        "reminders": db.collection(f"{user_data_path}/reminders")
    }

def init_firebase_auth():
    """Initializes Firebase authentication."""
    if not st.session_state.firebase_ready:
        try:
            auth = firebase_auth.get_auth()
            token = st.secrets.get("__initial_auth_token")

            # Sign in with custom token if provided, otherwise anonymously
            if token:
                user = auth.sign_in_with_custom_token(token)
                st.session_state.current_user_id = user.uid
                st.info(f"Signed in as authenticated user: {user.uid}")
            else:
                user = auth.sign_in_anonymously()
                st.session_state.current_user_id = user.uid
                st.warning(f"Signed in anonymously as: {user.uid}. Data is tied to this session.")
            st.session_state.firebase_ready = True
            st.rerun() # Rerun to load data once authenticated
        except Exception as e:
            st.error(f"Firebase Authentication Error: {e}")
            st.stop()

# Run Firebase auth setup only once
if not st.session_state.firebase_ready:
    init_firebase_auth()

# --- Load User Data from Firestore ---
if st.session_state.firebase_ready and st.session_state.current_user_id:
    collections = get_firestore_collections()

    # Load subjects
    if "user_subjects" not in st.session_state:
        st.session_state.user_subjects = []
        try:
            subjects_docs = collections["subjects"].stream()
            for doc in subjects_docs:
                st.session_state.user_subjects.append(doc.to_dict())
            if not st.session_state.user_subjects:
                # Add default subjects if none exist
                default_subjects = [
                    {"id": "general", "name": "General Chat", "emoji": "💬"},
                    {"id": str(uuid.uuid4()), "name": "Science", "emoji": "🔬"},
                    {"id": str(uuid.uuid4()), "name": "Maths", "emoji": "➕"},
                    {"id": str(uuid.uuid4()), "name": "Social Studies", "emoji": "🌍"},
                    {"id": str(uuid.uuid4()), "name": "Language", "emoji": "🗣️"},
                ]
                for subj in default_subjects:
                    collections["subjects"].document(subj["id"]).set(subj)
                    st.session_state.user_subjects.append(subj)
                st.rerun() # Rerun to display newly added subjects
        except Exception as e:
            st.error(f"Error loading subjects: {e}")

    # Load chat histories (optional: lazy load or load based on selected subject)
    # For simplicity, we will load history for the currently selected subject when needed.
    # We will use st.session_state.chat_histories as a cache.
    if "chat_histories_cache" not in st.session_state:
        st.session_state.chat_histories_cache = {}

    # Load learning progress
    if "learning_progress" not in st.session_state:
        try:
            progress_doc = collections["learning_progress"].document("main_progress").get()
            st.session_state.learning_progress = progress_doc.to_dict() if progress_doc.exists else {"lessons_completed": 0}
        except Exception as e:
            st.error(f"Error loading learning progress: {e}")
            st.session_state.learning_progress = {"lessons_completed": 0} # Default if error

    # Load reminders
    if "user_reminders" not in st.session_state:
        st.session_state.user_reminders = []
        try:
            reminders_docs = collections["reminders"].stream()
            for doc in reminders_docs:
                st.session_state.user_reminders.append(doc.to_dict())
        except Exception as e:
            st.error(f"Error loading reminders: {e}")

# --- Initialize Session State Variables (App-specific) ---
if "user_avatar" not in st.session_state:
    st.session_state["user_avatar"] = "😀" # Default emoji for the user
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "Home" # Default mode: Home (avatar selection)
if "selected_subject_id" not in st.session_state:
    st.session_state["selected_subject_id"] = "general" # Default to general chat

# --- Functions for Firestore Interactions ---
def add_message_to_firestore(subject_id, role, content):
    """Adds a message to the specified chat history in Firestore."""
    if not st.session_state.firebase_ready: return
    try:
        collections["chat_histories"].document(subject_id).collection("messages").add({
            "role": role,
            "content": content,
            "timestamp": firebase_firestore.SERVER_TIMESTAMP
        })
        # Update cache
        if subject_id in st.session_state.chat_histories_cache:
            st.session_state.chat_histories_cache[subject_id].append({"role": role, "content": content})
    except Exception as e:
        st.error(f"Error saving message to Firestore: {e}")

def load_chat_history_from_firestore(subject_id):
    """Loads chat history for a subject from Firestore."""
    if subject_id in st.session_state.chat_histories_cache:
        return st.session_state.chat_histories_cache[subject_id]
    
    if not st.session_state.firebase_ready: return []

    history = []
    try:
        messages_ref = collections["chat_histories"].document(subject_id).collection("messages")
        # Ordering by timestamp will require an index in Firestore.
        # For simplicity without index, we'll sort client-side after fetching.
        docs = messages_ref.order_by("timestamp").stream() # Requires a composite index on role and timestamp
        for doc in docs:
            history.append(doc.to_dict())
        st.session_state.chat_histories_cache[subject_id] = history
    except Exception as e:
        st.warning(f"Could not load chat history for {subject_id} (might need Firestore index or collection doesn't exist yet): {e}")
    return history

def add_subject_to_firestore(subject_name, emoji):
    """Adds a new subject to Firestore."""
    if not st.session_state.firebase_ready: return
    new_subject_id = str(uuid.uuid4())
    new_subject_data = {"id": new_subject_id, "name": subject_name, "emoji": emoji}
    try:
        collections["subjects"].document(new_subject_id).set(new_subject_data)
        st.session_state.user_subjects.append(new_subject_data)
        st.session_state.selected_subject_id = new_subject_id # Automatically select new subject
        st.toast(f"'{subject_name}' added! 🥳")
        st.rerun() # Rerun to update the sidebar subject list
    except Exception as e:
        st.error(f"Error adding subject: {e}")

def update_learning_progress(lessons_to_add=1):
    """Updates the user's learning progress."""
    if not st.session_state.firebase_ready: return
    current_lessons = st.session_state.learning_progress.get("lessons_completed", 0)
    new_lessons = current_lessons + lessons_to_add
    try:
        collections["learning_progress"].document("main_progress").set({"lessons_completed": new_lessons}, merge=True)
        st.session_state.learning_progress["lessons_completed"] = new_lessons
    except Exception as e:
        st.error(f"Error updating learning progress: {e}")

def add_reminder_to_firestore(reminder_text, reminder_type="Quiz", due_date=None):
    """Adds a new reminder to Firestore."""
    if not st.session_state.firebase_ready: return
    new_reminder_id = str(uuid.uuid4())
    reminder_data = {
        "id": new_reminder_id,
        "text": reminder_text,
        "type": reminder_type,
        "due_date": due_date.isoformat() if due_date else None, # Store as ISO string
        "created_at": firebase_firestore.SERVER_TIMESTAMP,
        "completed": False
    }
    try:
        collections["reminders"].document(new_reminder_id).set(reminder_data)
        st.session_state.user_reminders.append(reminder_data)
        st.toast(f"Reminder added: {reminder_text}! 🔔")
        st.rerun() # Rerun to display new reminder
    except Exception as e:
        st.error(f"Error adding reminder: {e}")


# --- Layout Structure ---
# Create 3 columns for main content layout: sidebar content (hidden by default, handled by Streamlit), main chat, and right panel
# Streamlit's native sidebar is handled by st.sidebar, so we structure the main layout with columns.
# We'll use 70/30 split for chat vs. subjects/games
main_col, right_panel_col = st.columns([0.7, 0.3]) # Adjust ratios as needed

# --- Sidebar for Navigation (Chat History and Mode Selection) ---
with st.sidebar:
    st.title("🫫live Bot")
    st.markdown("---") # Separator

    st.subheader("Your Avatar")
    st.markdown(f'<div style="font-size: 50px; text-align: center;">{st.session_state["user_avatar"]}</div>', unsafe_allow_html=True)
    if st.button("Change Friend", key="change_avatar_sidebar"):
        st.session_state["app_mode"] = "Home"
        st.session_state["current_chat_messages"] = [] # Clear chat history if changing avatar
        st.session_state["chat_histories_cache"] = {} # Clear cached history
        st.session_state["study_messages"] = {} # Clear study messages too
        st.rerun()
    st.markdown("---")

    st.subheader("What do you want to do?")
    selected_mode = st.radio(
        "Choose a section:",
        ("Chat with Bot", "Study Time", "Game Corner"),
        key="app_mode_radio"
    )
    st.session_state["app_mode"] = selected_mode # Update app_mode in session state

    st.markdown("---")
    st.subheader("Chat History")
    # Display subject-based chat history for easy switching
    # Ensure subjects are loaded before displaying
    if st.session_state.get("user_subjects"):
        subject_names = {subj["id"]: subj["name"] for subj in st.session_state.user_subjects}
        subject_emojis = {subj["id"]: subj["emoji"] for subj in st.session_state.user_subjects}

        selected_subject_name = st.radio(
            "Select Subject Chat:",
            options=[s["name"] for s in st.session_state.user_subjects],
            index=[s["name"] for s in st.session_state.user_subjects].index(subject_names.get(st.session_state.selected_subject_id, "General Chat")),
            format_func=lambda name: f"{subject_emojis[[s['name'] for s in st.session_state.user_subjects].index(name)]} {name}",
            key="subject_chat_selector"
        )
        st.session_state.selected_subject_id = next(s["id"] for s in st.session_state.user_subjects if s["name"] == selected_subject_name)
    else:
        st.info("Loading subjects...")

# --- Right Panel for Subjects, Games Icon, Reminders ---
with right_panel_col:
    # Games Icon (Top Right) - Conditional Access
    # Check if 'learning_progress' is loaded and lessons_completed threshold is met
    learning_progress_val = st.session_state.learning_progress.get("lessons_completed", 0) if st.session_state.firebase_ready else 0
    GAME_UNLOCK_THRESHOLD = 3 # Example: unlock after 3 lessons/chats

    if learning_progress_val >= GAME_UNLOCK_THRESHOLD:
        st.markdown(f'<div style="text-align: right; font-size: 40px; cursor: pointer;" title="Games unlocked!"><a href="#" onclick="window.parent.document.querySelector(\'[data-testid=\"stSidebarUserContent\"]\').scrollTop = 0; window.parent.document.querySelector(\'input[type=\"radio\"][value=\"Game Corner\"]\').click(); return false;">🎮</a></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: right; font-size: 12px; margin-top: -10px;">({learning_progress_val}/{GAME_UNLOCK_THRESHOLD} lessons for games)</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align: right; font-size: 40px; opacity: 0.5;" title="Complete {GAME_UNLOCK_THRESHOLD - learning_progress_val} more lessons to unlock games">🔒</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: right; font-size: 12px; margin-top: -10px;">({learning_progress_val}/{GAME_UNLOCK_THRESHOLD} lessons to unlock games)</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Your Subjects")
    if st.session_state.get("user_subjects"):
        for subject in st.session_state.user_subjects:
            st.markdown(f'{subject["emoji"]} {subject["name"]}')
    else:
        st.info("No subjects added yet.")

    with st.expander("Add New Subject"):
        new_subject_name = st.text_input("Subject Name")
        new_subject_emoji = st.text_input("Emoji (e.g., 🧪)", max_chars=2)
        if st.button("Add Subject") and new_subject_name:
            add_subject_to_firestore(new_subject_name, new_subject_emoji)

    st.markdown("---")
    st.subheader("Reminders")
    if st.session_state.get("user_reminders"):
        for reminder in st.session_state.user_reminders:
            status = "✅" if reminder.get("completed", False) else "⏰"
            st.info(f"{status} {reminder['text']} ({reminder.get('type', '')})")
    else:
        st.info("No reminders set yet.")


# --- Main Content Display ---
with main_col:
    # Display Home Screen (Avatar Selection)
    if st.session_state["app_mode"] == "Home":
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)
        st.title("Hey, I'm 🫒live! Choose Your Chat Friend!") # Updated greeting

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
            st.session_state["app_mode"] = "Chat with Bot" # Automatically switch to Chat mode after choosing avatar
            st.session_state["current_chat_messages"] = [] # Ensure general chat starts fresh
            st.session_state["selected_subject_id"] = "general" # Ensure 'General Chat' is selected
            st.rerun() # Rerun to switch to chat mode

    # --- Chat with Bot Section ---
    elif st.session_state["app_mode"] == "Chat with Bot":
        st.title(f"Let's Chat about {next((s['name'] for s in st.session_state.user_subjects if s['id'] == st.session_state.selected_subject_id), 'General Chat')}!")

        # Load chat history for the selected subject
        chat_history = load_chat_history_from_firestore(st.session_state.selected_subject_id)

        # Display chat messages for this mode
        for message in chat_history:
            avatar = "🫒" if message["role"] == "assistant" else st.session_state["user_avatar"]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Chat Input and Logic for general chat
        if prompt := st.chat_input("What do you want to talk about?"):
            # Add user message to current session state and Firestore
            chat_history.append({"role": "user", "content": prompt})
            add_message_to_firestore(st.session_state.selected_subject_id, "user", prompt)

            with st.chat_message("user", avatar=st.session_state["user_avatar"]):
                st.markdown(prompt)

            messages_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in chat_history # Use the loaded history for API context
            ]

            with st.chat_message("assistant", avatar="🫒"):
                # Create a placeholder for streamed response
                placeholder = st.empty()
                full_response_content = ""
                # Make the API call to Groq
                stream = client.chat.completions.create(
                    model="llama3-70b-8192", # Updated model
                    messages=messages_for_api,
                    stream=True,
                )
                # Iterate over the stream and update the placeholder
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response_content += chunk.choices[0].delta.content
                        placeholder.markdown(full_response_content + "▌") # Add blinking cursor for effect

                placeholder.markdown(full_response_content) # Display final content without cursor
            
            # Add assistant response to current session state and Firestore
            chat_history.append({"role": "assistant", "content": full_response_content})
            add_message_to_firestore(st.session_state.selected_subject_id, "assistant", full_response_content)
            
            # Increment learning progress for general chat or specific subject interaction
            update_learning_progress(lessons_to_add=1)
            st.rerun() # Rerun to refresh the chat history display

    # --- Study Time Section ---
    elif st.session_state["app_mode"] == "Study Time":
        st.title("📚 Study Time!")
        st.markdown("---")
        st.subheader(f"Learning in: {next((s['name'] for s in st.session_state.user_subjects if s['id'] == st.session_state.selected_subject_id), 'General Chat')}")

        # Ensure selected subject is not "general" for specific study context
        if st.session_state.selected_subject_id == "general":
            st.warning("Please select a specific subject from the sidebar to begin Study Time!")
        else:
            current_study_subject = next(s for s in st.session_state.user_subjects if s["id"] == st.session_state.selected_subject_id)
            
            # Load study messages for the current subject
            if current_study_subject["id"] not in st.session_state["study_messages"]:
                st.session_state["study_messages"][current_study_subject["id"]] = []
                initial_greeting = f"Hello! I'm your friendly {current_study_subject['name']} tutor. What would you like to learn about today?"
                st.session_state["study_messages"][current_study_subject["id"]].append({"role": "assistant", "content": initial_greeting})

            for message in st.session_state["study_messages"][current_study_subject["id"]]:
                avatar = "🫒" if message["role"] == "assistant" else st.session_state["user_avatar"]
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            if prompt := st.chat_input(f"Ask me about {current_study_subject['name']}..."):
                st.session_state["study_messages"][current_study_subject["id"]].append({"role": "user", "content": prompt})
                with st.chat_message("user", avatar=st.session_state["user_avatar"]):
                    st.markdown(prompt)

                system_prompt = f"You are a kind, patient, and knowledgeable tutor for kids learning about {current_study_subject['name']}. Explain concepts clearly, use simple language, and provide examples. Keep responses concise and engaging for a young audience. If the question is not about {current_study_subject['name']}, gently guide them back."

                messages_for_api = [{"role": "system", "content": system_prompt}] + \
                                   [{"role": m["role"], "content": m["content"]} for m in st.session_state["study_messages"][current_study_subject["id"]]]

                with st.chat_message("assistant", avatar="🫒"):
                    placeholder = st.empty()
                    full_response_content = ""
                    stream = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=messages_for_api,
                        stream=True,
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response_content += chunk.choices[0].delta.content
                            placeholder.markdown(full_response_content + "▌")
                    placeholder.markdown(full_response_content)
                st.session_state["study_messages"][current_study_subject["id"]].append({"role": "assistant", "content": full_response_content})
                update_learning_progress(lessons_to_add=1) # Increment for study lessons
                
                # Post-learning actions
                st.markdown("---")
                st.subheader("What's next?")
                col_post_learn_1, col_post_learn_2 = st.columns(2)
                with col_post_learn_1:
                    if st.button(f"Give me a Quiz on {current_study_subject['name']}!"):
                        st.session_state["app_mode"] = "Quiz Time"
                        st.session_state["quiz_subject_id"] = current_study_subject["id"]
                        add_reminder_to_firestore(f"Quiz time for {current_study_subject['name']}!", "Quiz")
                        st.rerun()
                with col_post_learn_2:
                    if st.button(f"Remind me to revise {current_study_subject['name']} later"):
                        # For simplicity, a reminder is added. You could add a date picker here.
                        add_reminder_to_firestore(f"Revise {current_study_subject['name']}", "Revision")
                        st.rerun()


    # --- Quiz Time Section ---
    elif st.session_state["app_mode"] == "Quiz Time":
        st.title("📝 Quiz Time!")
        st.markdown("---")
        quiz_subject_name = next((s['name'] for s in st.session_state.user_subjects if s['id'] == st.session_state.get('quiz_subject_id', 'general')), 'General Knowledge')
        st.subheader(f"Quiz on: {quiz_subject_name}")

        # Simplified Quiz Logic: Ask a random question based on chat history or subject
        if "quiz_question" not in st.session_state or st.button("New Quiz Question"):
            st.session_state.quiz_question = None
            st.session_state.quiz_answer = None

            # Attempt to generate a quiz question based on the subject
            messages_for_quiz_prompt = [
                {"role": "system", "content": f"You are a quiz master for kids. Generate a single, simple quiz question about '{quiz_subject_name}' with 3 multiple-choice options (A, B, C) and indicate the correct answer. Format: 'Question: ... A) ... B) ... C) ... Correct: [A/B/C]'"},
                {"role": "user", "content": f"Generate a quiz question about {quiz_subject_name}."}
            ]
            try:
                quiz_response = client.chat.completions.create(
                    model="llama3-8b-8192", # Use a lighter model for quizzes if preferred
                    messages=messages_for_quiz_prompt,
                    max_tokens=150
                )
                raw_quiz_content = quiz_response.choices[0].message.content
                st.session_state.quiz_question = raw_quiz_content
                st.session_state.quiz_answer = None # Reset answer
            except Exception as e:
                st.error(f"Error generating quiz question: {e}")
                st.session_state.quiz_question = "Could not generate a quiz question at this time. Please try again."

        if st.session_state.quiz_question:
            st.markdown(st.session_state.quiz_question)
            user_quiz_answer = st.text_input("Your Answer (e.g., A, B, or C)")
            if st.button("Submit Answer"):
                # Simple check for demo. In a real app, you'd parse Groq's output to verify.
                if st.session_state.quiz_question and ("Correct: " in st.session_state.quiz_question and user_quiz_answer.upper() in st.session_state.quiz_question.split("Correct:")[1]):
                    st.success("Correct! 🎉")
                else:
                    st.error("Not quite! Keep trying or ask for a new question.")
                # You might update learning progress or a quiz score here too.

        if st.button("Back to Study Time"):
            st.session_state["app_mode"] = "Study Time"
            st.rerun()

    # --- Game Corner Section ---
    elif st.session_state["app_mode"] == "Game Corner":
        st.title("🎮 Game Corner!")
        st.markdown("---")
        st.subheader("Welcome to the Game Corner!")
        st.markdown("This is where we'll add fun games to play.")
        st.markdown("---")

        if learning_progress_val >= GAME_UNLOCK_THRESHOLD:
            st.success("Games are unlocked! Choose one below:")
            st.write("- **One Player vs Bot:** Like a simple 'Guess the Number' or 'Rock-Paper-Scissors' with the computer.")
            st.write("- **Two Player Games:** Where two friends can play together on the same screen (e.g., Tic-Tac-Toe).")
            st.info("Actual game logic to be implemented here!")
        else:
            st.warning(f"Games are currently locked. Complete {GAME_UNLOCK_THRESHOLD - learning_progress_val} more lessons to unlock them! Current progress: {learning_progress_val}/{GAME_UNLOCK_THRESHOLD}")

        st.markdown("Stay tuned! If you have ideas for a game, let me know in the chat!")