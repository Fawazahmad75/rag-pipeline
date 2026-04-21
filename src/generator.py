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

# Factual chain
factual_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["factual_qa"]["system"]),
    ("human", prompts["factual_qa"]["human"])
])
factual_chain = factual_prompt | llm | StrOutputParser()

# Comparison chain
comparison_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["comparison_qa"]["system"]),
    ("human", prompts["comparison_qa"]["human"])
])
comparison_chain = comparison_prompt | llm | StrOutputParser()

def generate_answer(query: str, context_chunks: list, query_type: str = "factual") -> dict:
    context = "\n\n".join(context_chunks)
    chain = comparison_chain if query_type == "comparison" else factual_chain
    
    with collect_runs() as cb:
        answer = chain.invoke({"context": context, "question": query})
        run_id = cb.traced_runs[0].id if cb.traced_runs else None
    
    declined = "cannot find sufficient evidence" in answer.lower()
    
    # Build LangSmith trace URL
    trace_url = f"https://smith.langchain.com/public/{run_id}/r" if run_id else None

    return {
        "answer": answer,
        "declined": declined,
        "cited": not declined,
        "prompt_version": prompts["version"],
        "trace_url": trace_url
    }