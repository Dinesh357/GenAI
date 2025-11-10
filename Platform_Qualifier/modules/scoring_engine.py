from typing import Dict, List, Tuple


def compute_weighted_scores(items: List[Dict[str, object]],
                            eval_results: Dict[str, Dict[str, object]]
                            ) -> Tuple[List[Dict[str, object]], float]:
    """
    Compute weighted scores using parsed scores (0-3) and weights from checklist items.
    items: list of {criterion, question, weight}
    eval_results: criterion -> {score, justification}
    Returns (rows, total_weighted)
    """
    rows: List[Dict[str, object]] = []
    total = 0.0
    for it in items:
        crit = it.get("criterion")
        weight = float(it.get("weight") or 0)
        res = eval_results.get(crit, {})
        score = res.get("score") if isinstance(res, dict) else None
        try:
            s = int(score) if score is not None else 0
        except Exception:
            s = 0
        weighted = s * weight
        total += weighted
        rows.append({
            "criterion": crit,
            "question": it.get("question"),
            "score": s,
            "weight": weight,
            "weighted": weighted,
            "justification": res.get("justification") if isinstance(res, dict) else "",
        })
    return rows, total
