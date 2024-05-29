import os
import asyncio
import streamlit as st
import pdfkit
import markdown2
from io import BytesIO

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['TAVILY_API_KEY'] = st.secrets["OPENAI_API_KEY"]

from gpt_researcher import GPTResearcher

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def convert_markdown_to_pdf(markdown_text: str) -> BytesIO:
    html_text = markdown2.markdown(markdown_text)
    pdf = pdfkit.from_string(html_text, False)  # Create PDF from HTML string
    pdf_file = BytesIO(pdf)  # Create a BytesIO object from the PDF bytes
    pdf_file.seek(0)
    return pdf_file

report_type = "research_report"

st.title("GPT Researcher")
query = st.text_input("Enter your query")
filename = st.text_input("Enter filename for the PDF (without extension)", "report")

if st.button("Get Report"):
    if query:
        with st.spinner("Generating report..."):
            report_future = asyncio.create_task(get_report(query, report_type))
            report = asyncio.run(report_future)
            st.session_state["report"] = report
            st.markdown(st.session_state["report"])

            if st.button("Download Report as PDF"):
                pdf_file = convert_markdown_to_pdf(st.session_state["report"])
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=f"{filename}.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("Please enter a query")