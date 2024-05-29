import os
import asyncio
import streamlit as st
import markdown2
from io import BytesIO
from fpdf import FPDF

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['TAVILY_API_KEY'] = st.secrets["OPENAI_API_KEY"]

from gpt_researcher import GPTResearcher

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def convert_markdown_to_pdf(markdown_text: str) -> BytesIO:
    # Convert markdown to plain text
    plain_text = markdown2.markdown(markdown_text)
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    # Split the plain text into lines to add to the PDF
    lines = plain_text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    # Create a BytesIO buffer to hold the PDF data
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, 'F')  # Write PDF to the buffer
    pdf_buffer.seek(0)  # Move the cursor to the beginning of the buffer
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
        mime="application/octet-stream"  # Correct MIME type for PDF
    )