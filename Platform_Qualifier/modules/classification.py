
def classify_project(scores):
    weights = {key: 30 for key in scores}
    total_score = sum([scores[k] * weights.get(k, 0) for k in scores])
    if total_score > 850:
        return "Enterprise-grade Platform"
    elif total_score > 600:
        return "Emerging Platform"
    elif total_score > 300:
        return "Application / Modular Product"
    else:
        return "Application Development"
