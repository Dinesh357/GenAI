
def classify_project(total_score: float) -> str:
    if total_score > 850:
        return "Enterprise-grade Platform"
    elif total_score >= 601:
        return "Emerging Platform"
    elif total_score >= 301:
        return "Application / Modular Product"
    else:
        return "Application Development"
