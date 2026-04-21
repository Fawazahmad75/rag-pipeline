import os
import yaml
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tracers.context import collect_runs

load_dotenv()

with open("prompts.yaml") as f:
    prompts = yaml.safe_load(f)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

factual_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["factual_qa"]["system"]),
    ("human", prompts["factual_qa"]["human"])
])
factual_chain = factual_prompt | llm | StrOutputParser()

comparison_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["comparison_qa"]["system"]),
    ("human", prompts["comparison_qa"]["human"])
])
comparison_chain = comparison_prompt | llm | StrOutputParser()

# LangSmith identifiers
LANGSMITH_ORG = "b82502ba-8a75-4baf-ade6-c9cd3d444d53"
LANGSMITH_PROJECT = "865389ae-a511-49e0-b38a-beb32439d2e0"

def generate_answer(query: str, context_chunks: list, query_type: str = "factual") -> dict:
    context = "\n\n".join(context_chunks)
    chain = comparison_chain if query_type == "comparison" else factual_chain

    with collect_runs() as cb:
        answer = chain.invoke({"context": context, "question": query})
        run_id = cb.traced_runs[0].id if cb.traced_runs else None

    declined = "cannot find sufficient evidence" in answer.lower()

    trace_url = None
    if run_id:
        trace_url = f"https://smith.langchain.com/o/{LANGSMITH_ORG}/projects/p/{LANGSMITH_PROJECT}/r/{run_id}"

    return {
        "answer": answer,
        "declined": declined,
        "cited": not declined,
        "prompt_version": prompts["version"],
        "trace_url": trace_url
    }