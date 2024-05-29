import os
import asyncio
import streamlit as st
import markdown2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['TAVILY_API_KEY'] = st.secrets["OPENAI_API_KEY"]

from gpt_researcher import GPTResearcher

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def convert_markdown_to_pdf(markdown_text: str) -> BytesIO:
    # Convert markdown to HTML and strip HTML tags to get plain text
    plain_text = markdown2.markdown(markdown_text)
    # Create a BytesIO buffer to hold the PDF data
    pdf_buffer = BytesIO()
    # Create a canvas object using reportlab
    p = canvas.Canvas(pdf_buffer, pagesize=letter)
    # Split the plain text into lines to add to the PDF
    lines = plain_text.split('\n')
    # Start adding text to the PDF
    y = 750  # Initial position from the top
    for line in lines:
        p.drawString(30, y, line)
        y -= 15  # Move to the next line
    # Save the PDF into the buffer
    p.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def get_report_sync(query: str, report_type: str) -> str:
    return asyncio.run(get_report(query, report_type))

report_type = "research_report"

st.title("GPT Researcher")
query = st.text_input("Enter your query")
filename = st.text_input("Enter filename for the PDF (without extension)", "report")

if st.button("Get Report"):
    if query:
        with st.spinner("Generating report..."):
            report = get_report_sync(query, report_type)
            st.session_state["report"] = report
            st.session_state["filename"] = filename
            st.markdown(report)
    else:
        st.warning("Please enter a query")

if "report" in st.session_state:
    st.markdown(st.session_state["report"])
    pdf_file = convert_markdown_to_pdf(st.session_state["report"])
    st.download_button(
        label="Download PDF",
        data=pdf_file,
        file_name=f"{st.session_state['filename']}.pdf",
        mime="application/pdf"
    )