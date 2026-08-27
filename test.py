"""
Unit test for English Rice Pest and Disease Diagnosis Model.
"""

import model

test_cases = [
    {
        "description": "Stem damage indicators",
        "symptoms": [
            "Blackened_Grain_Balls",
            "Adult_Insects_Present",
            "Hook_Like_Root_Swelling",
            "Frass_In_Stem",
            "Brown_Planthopper_Present",
            "Deformed_Roots",
            "Bore_Holes_In_Stem"
        ]
    },
    {
        "description": "Root swelling and stunting indicators",
        "symptoms": [
            "Stunted_Growth",
            "Root_Knot_Swelling",
            "Brown_Planthopper_Present",
            "Whitehead_Empty_Panicles",
            "Hook_Like_Root_Swelling"
        ]
    }
]

for idx, case in enumerate(test_cases, 1):
    diagnosis = model.predict_diseases(case["symptoms"])
    print(f"Test Case #{idx} ({case['description']}):")
    print(f"  Input Symptoms : {case['symptoms']}")
    print(f"  Predicted Result: {diagnosis}\n")
