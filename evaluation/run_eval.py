import json
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_graph

# ── Load ground truth ──────────────────────────────────────────────────────────
with open("evaluation/ground_truth.json") as f:
    ground_truth = json.load(f)

print(f"Loaded {len(ground_truth)} questions")
print("Running evaluation...\n")

# ── Run each question through the pipeline ─────────────────────────────────────
results = []

for i, item in enumerate(ground_truth):
    question = item["question"]
    expected = item["ground_truth"]
    q_type = item["type"]

    print(f"[{i+1}/{len(ground_truth)}] {q_type.upper()}: {question[:60]}...")

    # Out of scope questions — just check if pipeline declined
    if q_type == "out_of_scope":
        try:
            graph = build_graph([])
            result = graph.invoke({
                "query": question,
                "query_type": "",
                "chunks": [],
                "metadata": [],
                "answer": "",
                "declined": False,
                "cited": False,
                "prompt_version": "",
                "retrieval_ms": 0.0,
                "generation_ms": 0.0
            })
            correctly_declined = result.get("declined", False)
            results.append({
                "question": question,
                "type": q_type,
                "answer": result.get("answer", ""),
                "ground_truth": expected,
                "correctly_declined": correctly_declined,
                "declined": result.get("declined", False),
                "cited": result.get("cited", False),
                "query_type_detected": result.get("query_type", ""),
                "retrieval_ms": result.get("retrieval_ms", 0),
                "generation_ms": result.get("generation_ms", 0),
                "prompt_version": result.get("prompt_version", ""),
                "faithfulness": 1.0 if correctly_declined else 0.0
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "question": question,
                "type": q_type,
                "answer": "",
                "ground_truth": expected,
                "correctly_declined": False,
                "declined": False,
                "cited": False,
                "query_type_detected": "",
                "retrieval_ms": 0,
                "generation_ms": 0,
                "prompt_version": "",
                "faithfulness": 0.0,
                "error": str(e)
            })
        time.sleep(1)  # rate limit protection
        continue

    # Factual and comparison questions
    try:
        graph = build_graph([])
        result = graph.invoke({
            "query": question,
            "query_type": "",
            "chunks": [],
            "metadata": [],
            "answer": "",
            "declined": False,
            "cited": False,
            "prompt_version": "",
            "retrieval_ms": 0.0,
            "generation_ms": 0.0
        })

        answer = result.get("answer", "")
        declined = result.get("declined", False)

        # Simple faithfulness check — does answer contain key terms from ground truth
        gt_words = set(expected.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(gt_words & answer_words) / max(len(gt_words), 1)
        faithfulness = min(overlap * 2, 1.0)  # scale overlap to 0-1

        results.append({
            "question": question,
            "type": q_type,
            "answer": answer,
            "ground_truth": expected,
            "correctly_declined": False,
            "declined": declined,
            "cited": result.get("cited", False),
            "query_type_detected": result.get("query_type", ""),
            "retrieval_ms": result.get("retrieval_ms", 0),
            "generation_ms": result.get("generation_ms", 0),
            "prompt_version": result.get("prompt_version", ""),
            "faithfulness": faithfulness
        })

        print(f"  Query type detected: {result.get('query_type', 'unknown')}")
        print(f"  Faithfulness score: {faithfulness:.2f}")
        print(f"  Declined: {declined}")

    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({
            "question": question,
            "type": q_type,
            "answer": "",
            "ground_truth": expected,
            "correctly_declined": False,
            "declined": False,
            "cited": False,
            "query_type_detected": "",
            "retrieval_ms": 0,
            "generation_ms": 0,
            "prompt_version": "",
            "faithfulness": 0.0,
            "error": str(e)
        })

    time.sleep(2)  # rate limit protection between questions

# ── Save results ───────────────────────────────────────────────────────────────
with open("evaluation/results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n" + "="*60)
print("EVALUATION SUMMARY")
print("="*60)

# Overall metrics
total = len(results)
factual = [r for r in results if r["type"] == "factual"]
comparison = [r for r in results if r["type"] == "comparison"]
out_of_scope = [r for r in results if r["type"] == "out_of_scope"]

avg_faithfulness = sum(r["faithfulness"] for r in results) / total
factual_faith = sum(r["faithfulness"] for r in factual) / max(len(factual), 1)
comparison_faith = sum(r["faithfulness"] for r in comparison) / max(len(comparison), 1)
out_of_scope_correct = sum(1 for r in out_of_scope if r.get("correctly_declined")) / max(len(out_of_scope), 1)

citation_rate = sum(1 for r in results if r["cited"]) / total
decline_rate = sum(1 for r in results if r["declined"]) / total

avg_retrieval = sum(r["retrieval_ms"] for r in results) / total
avg_generation = sum(r["generation_ms"] for r in results) / total

print(f"Total questions:        {total}")
print(f"Factual questions:      {len(factual)}")
print(f"Comparison questions:   {len(comparison)}")
print(f"Out of scope questions: {len(out_of_scope)}")
print(f"")
print(f"Avg faithfulness:       {avg_faithfulness:.2f}")
print(f"Factual faithfulness:   {factual_faith:.2f}")
print(f"Comparison faithfulness:{comparison_faith:.2f}")
print(f"Out of scope accuracy:  {out_of_scope_correct:.2%}")
print(f"")
print(f"Citation coverage:      {citation_rate:.2%}")
print(f"Decline rate:           {decline_rate:.2%}")
print(f"")
print(f"Avg retrieval time:     {avg_retrieval:.1f}ms")
print(f"Avg generation time:    {avg_generation:.1f}ms")
print(f"")
print(f"Results saved to evaluation/results.json")

# ── CI gate ────────────────────────────────────────────────────────────────────
FAITHFULNESS_THRESHOLD = 0.75

if avg_faithfulness < FAITHFULNESS_THRESHOLD:
    print(f"\n❌ FAILED: Faithfulness {avg_faithfulness:.2f} below threshold {FAITHFULNESS_THRESHOLD}")
    sys.exit(1)
else:
    print(f"\n✅ PASSED: Faithfulness {avg_faithfulness:.2f} above threshold {FAITHFULNESS_THRESHOLD}")
    sys.exit(0)