class Rule:
    def __init__(self, id, category, field, operator, value, risk, message, suggestion, condition=None):
        self.id = id
        self.category = category
        self.field = field
        self.operator = operator
        self.value = value
        self.risk = risk
        self.message = message
        self.suggestion = suggestion
        self.condition = condition

    def __repr__(self):
        return f"Rule(id={self.id}, category={self.category}, risk={self.risk})"
