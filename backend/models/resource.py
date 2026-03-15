class Resource:
    def __init__(self, id, type, usage, public, encrypted, cost, logging, role):
        self.id = id
        self.type = type
        self.usage = usage
        self.public = public
        self.encrypted = encrypted
        self.cost = cost
        self.logging = logging
        self.role = role

    def __repr__(self):
        return f"Resource(id={self.id}, type={self.type}, usage={self.usage}%, cost=${self.cost})"
