import streamlit as st
import requests
from backend.graph import bot, headingbot
from backend.memory import (
    retrieve_threads,
    thread_document_metadata
)
from backend.rag import ingest_pdf

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)
import uuid
import os 
from langsmith import traceable

os.environ['LANGCHAIN_PROJECT']='comeonchat_langsmith'

# *********************************** Utility Functions ****************************************** #
@traceable
def generate_thread_id():
    return str(uuid.uuid4())

@traceable
def reset_chat():
    new_thread_id=generate_thread_id()
    st.session_state['thread_id']=new_thread_id
    st.session_state['message_history']=[]
    if new_thread_id not in st.session_state['threads_list']: 
        st.session_state['threads_list'].append(new_thread_id)
    st.rerun()

@traceable
def load_conversation(thread_id):
    state = bot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )
    return state.values.get('messages', [])

@traceable
def generate_name(thread_id):
    if str(thread_id) in st.session_state['thread_titles']:
        return st.session_state['thread_titles'][str(thread_id)]
    
    data= bot.get_state(
        config={'configurable':{'thread_id': thread_id}}
    ).values.get('messages',[])
    # state = bot.get_state({'configurable':{'thread_id':{thread_id}}})
    # messages = state.values.get("messages", [])
    user_data=""
    user_data = " ".join(
    m.content for m in data if isinstance(m, HumanMessage)
    )[:80]
    
    if not user_data.strip():
        return "New Chat"
    prompt = f"""Generate a short conversation title (3-6 words). Conversation:{user_data}"""
    name = headingbot.invoke(prompt)
    st.session_state['thread_titles'][str(thread_id)]=name.heading
    return name.heading


if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles']={}
   
if 'threads_list' not in st.session_state:
    st.session_state['threads_list']=retrieve_threads()

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
if 'thread_id' not in st.session_state:
    thread=generate_thread_id()
    st.session_state['thread_id']= thread
    if thread not in st.session_state['threads_list']:
        st.session_state['threads_list'].append(thread)
        
if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}
thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["threads_list"][::-1]
selected_thread = None



CONFIG={
    'configurable':{
        'thread_id': str(st.session_state['thread_id'])
    },
    'metadata':{
        'thread_id': str(st.session_state['thread_id'])
    },
    'run_name':'comeonchat_chatbot'
}

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


st.sidebar.title('ComeOnChat 💬') 
st.sidebar.markdown(f"**Thread ID:** `{thread_key}`")

if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    st.sidebar.success(
        f"Using `{latest_doc.get('filename')}` "
        f"({latest_doc.get('chunks')} chunks from {latest_doc.get('documents')} pages)"
    )
else:
    st.sidebar.info("No PDF indexed yet.")

uploaded_pdf = st.sidebar.file_uploader("Upload a PDF for this chat", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"`{uploaded_pdf.name}` already processed for this chat.")
    else:
        with st.sidebar.status("Indexing PDF…", expanded=True) as status_box:

            files = {"file": uploaded_pdf}
            data = {"thread_id": thread_key}

            response = requests.post(
                "http://127.0.0.1:8000/upload-pdf",
                params={"thread_id": thread_key},
                files={
                    "file": (
                        uploaded_pdf.name,
                        uploaded_pdf.getvalue(),
                        "application/pdf"
                    )
                }
            )

            data = response.json()

            if response.status_code == 200:
                result = data["metadata"]
                thread_docs[uploaded_pdf.name] = result
            else:
                st.error(data)

            status_box.update(label="✅ PDF indexed", state="complete", expanded=False)

user_input= st.chat_input('Type here:')
if user_input:
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        def ai_only_stream():
            with requests.post(
                "http://127.0.0.1:8000/chat/stream",
                json={
                    "message": user_input,
                    "thread_id": thread_key
                },
                stream=True
            ) as response:

                for chunk in response.iter_content(decode_unicode=True):
                    if chunk:
                        yield chunk
        
        ai_message= st.write_stream(ai_only_stream())        
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})

    response = requests.get(
        f"http://127.0.0.1:8000/thread/{thread_key}/metadata"
    )

    doc_meta = response.json()
    if doc_meta:
        st.caption(
            f"Document indexed: {doc_meta.get('filename')} "
            f"(chunks: {doc_meta.get('chunks')}, pages: {doc_meta.get('documents')})"
        )

st.divider()

if selected_thread:
    st.session_state["thread_id"] = selected_thread
    messages = load_conversation(selected_thread)

    temp_messages = []
    for msg in messages:
        role = ""
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue
        temp_messages.append({"role": role, "content": msg.content})
    st.session_state["message_history"] = temp_messages
    st.session_state["ingested_docs"].setdefault(str(selected_thread), {})
    st.rerun() 
    
with st.sidebar:
    if st.button("New Chat", type="primary"):
        reset_chat()
    st.header('My conversations')
    for i, thread_id in enumerate(st.session_state['threads_list'][::-1]):
        thread_heading = generate_name(thread_id)

        if st.button(thread_heading, key=f"thread_btn_{thread_id}"):

            st.session_state['thread_id'] = thread_id

            message_data = load_conversation(thread_id)

            message_container = []
            for message in message_data:

                if isinstance(message, HumanMessage):
                    role = "user"
                elif isinstance(message, AIMessage):
                    role = "assistant"
                else:
                    continue

                message_container.append(
                    {
                        "role": role,
                        "content": message.content
                    }
                )

            st.session_state['message_history'] = message_container

            st.rerun()
            