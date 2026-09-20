"""Curated eval set for Ragas (spec §14: Ragas faithfulness >= 0.80 CI gate).

Fixed, hand-written questions + ground truths against our 3 seed documents
(seed_data/*.txt, *.pdf) — NOT real user queries. See conversation notes:
CI-gate evals need a repeatable, comparable test set with known-correct
answers, which live user queries can't provide.
"""

RAG_EVAL_CASES: list[dict[str, str]] = [
    {
        "question": "What caused the budget overrun in the roads department?",
        "ground_truth": (
            "The roads department had a 12% budget overrun on the resurfacing "
            "project due to material cost inflation, covered by reallocating "
            "Rs 8 lakh from the contingency fund."
        ),
    },
    {
        "question": "How many new engineer positions were approved for the roads department?",
        "ground_truth": (
            "3 new junior engineer positions were approved for the roads "
            "department to reduce project delays."
        ),
    },
    {
        "question": "What is the status of Smart City phase 2 funding?",
        "ground_truth": (
            "Smart City phase 2 funding was pending state finance committee "
            "approval, and was later approved, with a work order to be issued "
            "to the vendor within 10 days."
        ),
    },
    {
        "question": "What were the results of the smart traffic signal pilot?",
        "ground_truth": (
            "The 5-junction smart traffic signal pilot reduced average wait "
            "time by 18%, and expansion to 15 more junctions was recommended."
        ),
    },
    {
        "question": "Why is adoption of the citizen feedback portal low?",
        "ground_truth": (
            "Only 3% of complaints are filed through the online citizen "
            "feedback portal; an awareness campaign with the IT cell was "
            "proposed to improve adoption."
        ),
    },
    {
        "question": "What caused the delay in the Sector 22 road resurfacing project?",
        "ground_truth": (
            "The Sector 22 road resurfacing project was delayed by two weeks "
            "due to monsoon conditions, with revised completion by the end of "
            "next month."
        ),
    },
    {
        "question": "What water supply issue was reported in Sector 15?",
        "ground_truth": (
            "Residents in Sector 15 complained about low water pressure during "
            "morning hours; the team agreed to investigate the pumping "
            "station capacity."
        ),
    },
    {
        "question": "What is planned for the public park renovation?",
        "ground_truth": (
            "The park renovation near the community center plans to add new "
            "benches, solar lighting, and a children's play area, pending "
            "finance wing budget approval."
        ),
    },
    {
        "question": "What safety concern was raised near the Sector 22 construction zone?",
        "ground_truth": (
            "Members raised concerns about pedestrian safety near the "
            "construction zone and asked for additional barricades to be "
            "installed immediately."
        ),
    },
    {
        "question": "How much of the northern sectors water pipeline has been laid?",
        "ground_truth": (
            "The new water pipeline for the northern sectors has been laid "
            "across sixty percent of the planned route."
        ),
    },
]
