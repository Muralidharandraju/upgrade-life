import streamlit as st
import PyPDF2 as pdf
from ollama import generate



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




# prompt_template = """ You are a helpfull assistant. Analyze the provided text and identify its primary subject.
# Summarize the content in bullet points, highlighting the background, main discussion points, key findings,
# and any relevant conclusions drawn from the text.

# text : {}

# I want the response in one single string in below format
# {{"Topic Name": "",
# "Summary on Topic":""}}

# """


prompt_template = """ You are a helpfull assistant. Analyze the provided text and identify its primary subject.
Summarize the content in bullet points, highlighting the background, main discussion points, key findings,
and any relevant conclusions drawn from the text.

text : {}

"""


## Creating the Streamlit App
st.title("Smart Summary")
uploaded_file=st.file_uploader("Upload your pdf document for summary",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text=input_pdf_text(uploaded_file)
        prompt_text = prompt_template.format(text)
        output= generate(model='gemma3', prompt=prompt_text)
        st.subheader(output.response)



