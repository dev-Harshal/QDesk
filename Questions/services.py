def classify_blooms_taxonomy(question):
    taxonomy_keywords = {
        "Remember": ["define", "list", "recall", "name", "identify", "state", "who", "what", "when", "where", "how", "which"],
        "Understand": ["explain", "describe", "summarize", "interpret", "classify", "compare", "contrast"],
        "Apply": ["apply", "demonstrate", "solve", "use", "calculate", "implement", "illustrate"],
        "Analyze": ["analyze", "differentiate", "distinguish", "examine", "break down", "categorize", "infer"],
        "Evaluate": ["evaluate", "judge", "assess", "defend", "justify", "argue", "critique", "difference"],
        "Create": ["create", "design", "develop", "formulate", "compose", "construct", "synthesize", "plan"]
    }

    question = question.lower()
    matched_levels = []

    # Find all matching taxonomy levels for the question
    for level, keywords in taxonomy_keywords.items():
        if any(keyword in question for keyword in keywords):
            matched_levels.append(level.title())

    # Return the levels as a comma-separated string or "Indefinable"
    return ', '.join(matched_levels) if matched_levels else "Indefinable"