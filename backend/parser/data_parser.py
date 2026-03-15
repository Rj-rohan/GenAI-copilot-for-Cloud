import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.resource import Resource

class DataParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        
        resources = []
        for item in data:
            resource = Resource(
                id=item['id'],
                type=item['type'],
                usage=item['usage'],
                public=item['public'],
                encrypted=item['encrypted'],
                cost=item['cost'],
                logging=item['logging'],
                role=item['role']
            )
            resources.append(resource)
        
        return resources
