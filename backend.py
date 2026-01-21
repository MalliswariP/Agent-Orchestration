from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic import hub


app = FastAPI()

class Query(BaseModel):
    query: str


# ================== GOOGLE KEY FIX ==================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ================== LLM ==================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


# ================== TOOLS ==================
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
web = DuckDuckGoSearchRun()
arxiv = ArxivQueryRun()

tools = [wiki, web, arxiv]


# ================== PROMPT ==================
prompt = hub.pull("hwchase17/react")


# ================== RESEARCH AGENT ==================
research_agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

research_exec = AgentExecutor(
    agent=research_agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True
)


# ================== SUMMARIZER ==================
def summarizer_agent(content: str) -> str:
    prompt = f"""
Act as a professional research summarization agent.

Using the content below, generate a structured academic summary with:

1. Topic Overview
2. Background Context
3. Core Concepts
4. Use-cases
5. Advantages
6. Challenges
7. Future Scope
8. Conclusion

Content:
\"\"\"{content}\"\"\"
"""
    response = llm.invoke(prompt)
    return response.content


# ================== EMAIL ==================
def email_agent(content: str) -> str:
    first_line = content.split(".")[0][:60]
    subject = f"Subject: Overview on {first_line}"

    return f"""
{subject}

Dear Sir/Madam,

{content}

Regards,
Multi-Agent Research System
"""


# ================== ARXIV TRIM ==================
def trim_arxiv_output(raw_text: str) -> str:
    lines = raw_text.split("\n")
    papers = [ln.strip() for ln in lines if ln.strip()]
    return "\n".join(papers[:5])


# ================== MAIN PIPELINE ==================
@app.post("/run")
async def run_pipeline(payload: Query) -> Dict[str, Any]:

    query = payload.query
    raw_output = query

    # ---- STEP 1: RESEARCH ----
    try:
        result = research_exec.invoke({"input": query})
        raw_output = result.get("output", query)

        arxiv_trim = trim_arxiv_output(raw_output) if "arxiv" in raw_output.lower() else None

        research_block = {
            "wiki_web": raw_output,
            "arxiv": arxiv_trim
        }

    except Exception:
        research_block = {
            "wiki_web": query,
            "arxiv": None
        }

    # ---- STEP 2: SUMMARY ----
    summary_block = summarizer_agent(raw_output)

    # ---- STEP 3: EMAIL ----
    email_block = email_agent(summary_block)

    return {
        "research": research_block,
        "summary": summary_block,
        "email": email_block
    }


# ================== CLOUD DEPLOYMENT FIX ==================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
