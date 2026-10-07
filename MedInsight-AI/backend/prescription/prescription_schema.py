REQUIRED_FIELDS = ("strength", "frequency")           # missing => human review
OPTIONAL_FIELDS = ("duration", "form_or_quantity", "timing")  # missing => warning only

# Confidence weights (sum 1.0). Drug identity + strength + frequency carry the safety weight.
WEIGHTS = {"drug": 0.40, "strength": 0.25, "frequency": 0.25,
           "duration": 0.04, "form_or_quantity": 0.03, "timing": 0.03}
