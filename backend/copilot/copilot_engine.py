import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot.query_handler import QueryHandler
from copilot.context_builder import ContextBuilder
from copilot.prompt_generator import PromptGenerator
from copilot.llm_connector import LLMConnector

class CopilotEngine:
    def __init__(self, findings_path=None, use_mock_llm=True):
        self.query_handler = QueryHandler()
        self.context_builder = ContextBuilder(findings_path)
        self.prompt_generator = PromptGenerator()
        self.llm_connector = LLMConnector(use_mock=use_mock_llm)

    def process_query(self, user_query):
        # Step 1: Parse query
        parsed_query = self.query_handler.parse_query(user_query)
        
        # Step 2: Build context
        if parsed_query['type'] == 'summary':
            context = self.context_builder.get_summary_stats()
        else:
            context = self.context_builder.build_context(parsed_query)
        
        # Step 3: Generate prompt
        prompt = self.prompt_generator.generate_prompt(parsed_query['type'], context)
        
        # Step 4: Get LLM response
        response = self.llm_connector.generate_response(prompt, parsed_query['type'], context)
        
        return {
            'query': user_query,
            'query_type': parsed_query['type'],
            'response': response,
            'context_count': context.get('count', 0)
        }

    def get_available_commands(self):
        return """
AVAILABLE COMMANDS:

FILTERING:
  - "show high risk" - Display high priority findings
  - "show critical" - Display critical findings
  - "show cost issues" - Display cost optimization opportunities
  - "show security" - Display security vulnerabilities
  - "show storage" - Display storage resource issues

ANALYSIS:
  - "explain r3" - Explain why resource r3 is flagged
  - "why is r3 critical" - Detailed risk analysis

REMEDIATION:
  - "fix r3" - Get step-by-step fix instructions
  - "how to fix r3" - Remediation guidance

REPORTING:
  - "summary" - Executive summary report
  - "report" - Full analysis report
  - "total cost" - Cost impact analysis

EXAMPLES:
  > show critical
  > explain r3
  > fix r3
  > summary
"""
