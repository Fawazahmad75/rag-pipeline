@app.get("/metrics")
async def get_metrics():
    import json
    import numpy as np
    metrics_file = "metrics.json"
    if not os.path.exists(metrics_file):
        return {"metrics": [], "summary": {}}
    with open(metrics_file) as f:
        metrics = json.load(f)
    if not metrics:
        return {"metrics": [], "summary": {}}
    
    latencies = [m["total_ms"] for m in metrics]
    p50 = round(float(np.percentile(latencies, 50)), 1)
    p95 = round(float(np.percentile(latencies, 95)), 1)
    total = len(metrics)
    cited = sum(1 for m in metrics if m["cited"])
    declined = sum(1 for m in metrics if m["declined"])

    return {
        "metrics": metrics[-20:],  # last 20 queries
        "summary": {
            "total_queries": total,
            "citation_rate": round(cited / total * 100, 1),
            "decline_rate": round(declined / total * 100, 1),
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "avg_retrieval_ms": round(sum(m["retrieval_ms"] for m in metrics) / total, 1),
            "avg_generation_ms": round(sum(m["generation_ms"] for m in metrics) / total, 1)
        }
    }