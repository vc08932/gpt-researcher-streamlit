import os
import asyncio
import streamlit as st

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['TAVILY_API_KEY'] = st.secrets["OPENAI_API_KEY"]

from gpt_researcher import GPTResearcher

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    return report

report_type = "research_report"

st.title("GPT Researcher")
query = st.text_input("Enter your query")
if st.button("Get Report"):
    report = asyncio.run(get_report(query, report_type))
    st.markdown(report)



