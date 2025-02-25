import os
import asyncio
import streamlit as st
import markdown2
from io import BytesIO
from fpdf import FPDF

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['OPENAI_BASE_URL'] = st.secrets["OPENAI_BASE_URL"]
os.environ['TAVILY_API_KEY'] = st.secrets["TAVILY_API_KEY"]

from gpt_researcher import GPTResearcher

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def convert_markdown_to_pdf(markdown_text: str) -> BytesIO:
    plain_text = markdown2.markdown(markdown_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    lines = plain_text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

async def main(query: str, report_type: str):
    report = await get_report(query, report_type)
    st.session_state["report"] = report
    st.experimental_rerun()

report_type = "research_report"

st.title("GPT Researcher")
query = st.text_input("Enter your query")
filename = st.text_input("Enter filename for the PDF (without extension)", "report")

if st.button("Get Report"):
    if query:
        with st.spinner("Generating report..."):
            asyncio.run(main(query, report_type))
    else:
        st.warning("Please enter a query")

if "report" in st.session_state:
    st.markdown(st.session_state["report"])
    pdf_file = convert_markdown_to_pdf(st.session_state["report"])
    st.download_button(
        label="Download PDF",
        data=pdf_file,
        file_name=f"{filename}.pdf",
        mime="application/pdf"
    )
