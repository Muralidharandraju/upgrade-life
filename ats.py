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


#Prompt Template --> The Better the prompt better is the result
prompt_template="""
Hey Act Like a skilled or very experienced ATS(Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide the best assistance for improving the resumes. Assign the percentage Matching based on the Job description and the missing keywords with high accuracy.  
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

## Creating the Streamlit App
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")


if submit:
    if uploaded_file is not None:
        text=input_pdf_text(uploaded_file)
        prompt_text = prompt_template.format(text=text,jd=jd)
        output= generate(model='gemma3', prompt=prompt_text)
        st.subheader(output.response)


