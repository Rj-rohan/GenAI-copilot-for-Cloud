import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.rule import Rule

class RuleLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        
        rules = []
        for item in data:
            rule = Rule(
                id=item['id'],
                category=item['category'],
                field=item['field'],
                operator=item['operator'],
                value=item['value'],
                risk=item['risk'],
                message=item['message'],
                suggestion=item['suggestion'],
                condition=item.get('condition')
            )
            rules.append(rule)
        
        return rules
