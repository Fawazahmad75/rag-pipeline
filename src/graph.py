import time
import yaml
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.retriever import hybrid_search, vector_search, rerank
from src.generator import generate_answer, llm
import os
from dotenv import load_dotenv

load_dotenv()

with open("prompts.yaml") as f:
    prompts = yaml.safe_load(f)

# --- State Definition ---
class RAGState(TypedDict):
    query: str
    query_type: str
    chunks: list
    metadata: list
    answer: str
    declined: bool
    cited: bool
    prompt_version: str
    retrieval_ms: float
    generation_ms: float

# --- Router Node ---
router_prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["router"]["system"]),
    ("human", "{query}")
])
router_chain = router_prompt | llm | StrOutputParser()

def router_node(state: RAGState) -> dict:
    query_type = router_chain.invoke({"query": state["query"]}).strip().lower()
    # Sanitize — model might return something unexpected
    if query_type not in ["factual", "comparison", "out_of_scope"]:
        query_type = "factual"
    return {"query_type": query_type}

# --- Retrieval Nodes ---
def factual_node(state: RAGState, all_chunks: list) -> dict:
    start = time.time()
    chunks, metadata = hybrid_search(state["query"], all_chunks, n_results=5)
    retrieval_ms = round((time.time() - start) * 1000, 1)
    return {"chunks": chunks, "metadata": metadata, "retrieval_ms": retrieval_ms}

def comparison_node(state: RAGState, all_chunks: list) -> dict:
    start = time.time()
    chunks, metadata = hybrid_search(state["query"], all_chunks, n_results=7)
    retrieval_ms = round((time.time() - start) * 1000, 1)
    return {"chunks": chunks, "metadata": metadata, "retrieval_ms": retrieval_ms}

# --- Generation Node ---
def generation_node(state: RAGState) -> dict:
    start = time.time()
    result = generate_answer(state["query"], state["chunks"], state["query_type"])
    generation_ms = round((time.time() - start) * 1000, 1)
    return {
        "answer": result["answer"],
        "declined": result["declined"],
        "cited": result["cited"],
        "prompt_version": result["prompt_version"],
        "generation_ms": generation_ms
    }

# --- Out of Scope Node ---
def out_of_scope_node(state: RAGState) -> dict:
    return {
        "answer": "I can only answer questions related to financial documents. This question appears to be out of scope.",
        "declined": True,
        "cited": False,
        "chunks": [],
        "metadata": [],
        "retrieval_ms": 0.0,
        "generation_ms": 0.0,
        "prompt_version": prompts["version"]
    }

# --- Routing Logic ---
def route_query(state: RAGState) -> str:
    return state["query_type"]

# --- Build Graph ---
def build_graph(all_chunks: list):
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("factual", lambda s: factual_node(s, all_chunks))
    graph.add_node("comparison", lambda s: comparison_node(s, all_chunks))
    graph.add_node("out_of_scope", out_of_scope_node)
    graph.add_node("generate", generation_node)

    # Entry point
    graph.set_entry_point("router")

    # Conditional edges from router
    graph.add_conditional_edges("router", route_query, {
        "factual": "factual",
        "comparison": "comparison",
        "out_of_scope": "out_of_scope"
    })

    # factual and comparison both go to generation
    graph.add_edge("factual", "generate")
    graph.add_edge("comparison", "generate")

    # generation and out_of_scope both end
    graph.add_edge("generate", END)
    graph.add_edge("out_of_scope", END)

    return graph.compile()