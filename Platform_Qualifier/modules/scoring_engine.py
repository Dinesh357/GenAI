def compute_scores(answers):
    # Define keyword patterns for scoring
    scoring_keywords = {
        3: ["multi-use", "reusable", "scalable", "ecosystem", "shared", "extensible", "multi-tenant"],
        2: ["partial", "some reuse", "limited extensibility", "moderate", "basic"],
        1: ["minimal", "specific", "single use", "low"],
        0: ["not applicable", "not present", "none"]
    }

    scores = {}
    for criterion, answer in answers.items():
        score = 0  # Default score
        answer_lower = answer.lower()
        for s, keywords in scoring_keywords.items():
            if any(keyword in answer_lower for keyword in keywords):
                score = s
                break
        scores[criterion] = score

    return scores
