import streamlit as st
import PyPDF2 as pdf
# Changed import to use the full ollama module for chat functionality
import ollama


# Extract and concatenate text from all pages of the given PDF file
def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    # Iterate through all the pages
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        # Extracting the text
        text+=str(page.extract_text())
    return text

# Prompt template for summarization
summary_prompt_template = """ You are a helpfull assistant. Analyze the provided text and identify its primary subject.
Summarize the content in bullet points, highlighting the background, main discussion points, key findings,
and any relevant conclusions drawn from the text.

text : {}
"""

# Initialize session state variables
if "summary_generated" not in st.session_state:
    st.session_state.summary_generated = False
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "document_summary" not in st.session_state:
    st.session_state.document_summary = None
if "messages" not in st.session_state:  # For chat messages
    st.session_state.messages = []
if "full_chat_response" not in st.session_state: # To accumulate streamed chat response
    st.session_state.full_chat_response = ""

## Creating the Streamlit App
st.title("Smart Summary with Chat")
uploaded_file=st.file_uploader("Upload your PDF document",type="pdf",help="Please uplaod the pdf")

submit_summary = st.button("Generate Summary and Start Chat")

if submit_summary and uploaded_file is not None:
    # Reset states if a new file is submitted or process is restarted
    st.session_state.messages = []
    st.session_state.summary_generated = False
    st.session_state.document_text = None
    st.session_state.document_summary = None

    text = input_pdf_text(uploaded_file)
    st.session_state.document_text = text

    if text and text.strip(): # Ensure text was extracted and is not empty
        summary_prompt = summary_prompt_template.format(text)
        try:
            # Use ollama.generate for the initial summary
            response = ollama.generate(model='gemma3', prompt=summary_prompt)
            st.session_state.document_summary = response['response']
            st.session_state.summary_generated = True
            # Initialize chat messages after summary
            st.session_state.messages = [
                {"role": "assistant", "content": "Summary generated. You can now ask questions about the document."}
            ]
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            st.session_state.summary_generated = False
    else:
        st.warning("Could not extract text from the PDF or the PDF is empty.")
        st.session_state.summary_generated = False

# Display summary if it has been generated and stored
if st.session_state.get("document_summary"):
    st.subheader("Summary:")
    st.write(st.session_state.document_summary)

# Chat functionality (if summary has been generated and document text is available)
if st.session_state.get("summary_generated") and st.session_state.get("document_text"):
    st.divider()
    st.subheader("Chat about the Document")

    # Display existing chat messages
    for msg in st.session_state.messages:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

    # Generator for Streaming Chat Tokens
    def generate_chat_stream():
        system_prompt = {
            "role": "system",
            "content": f"You are a helpful assistant. Answer questions based on the following document content. Be concise and refer to the document when relevant.\n\n---DOCUMENT START---\n{st.session_state.document_text}\n---DOCUMENT END---"
        }
        messages_for_ollama = [system_prompt] + st.session_state.messages
        
        response_stream = ollama.chat(
            model='gemma3',
            messages=messages_for_ollama,
            stream=True
        )
        
        st.session_state.full_chat_response = "" # Clear before accumulating new response
        for partial_resp in response_stream:
            token = partial_resp.get("message", {}).get("content", "")
            if token:
                st.session_state.full_chat_response += token
                yield token

    if prompt := st.chat_input("Ask a question about the document..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="🧑‍💻").write(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            st.write_stream(generate_chat_stream)
        
        if st.session_state.full_chat_response:
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.full_chat_response})
            st.session_state.full_chat_response = "" # Clear after use

    if uploaded_file is not None:
        pass
