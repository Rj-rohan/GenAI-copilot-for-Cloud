import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot.copilot_engine import CopilotEngine

def print_banner():
    print("\n" + "=" * 80)
    print("  GENAI-POWERED CLOUD SECURITY COPILOT")
    print("  Risk & Cost Optimization Advisor")
    print("=" * 80)

def print_help():
    copilot = CopilotEngine()
    print(copilot.get_available_commands())

def main():
    print_banner()
    
    copilot = CopilotEngine()
    
    print("\nType 'help' for available commands, 'quit' to exit\n")
    
    # Demo queries
    demo_queries = [
        "show critical",
        "explain r3",
        "fix r3",
        "summary"
    ]
    
    print("DEMO MODE - Running sample queries:\n")
    
    for query in demo_queries:
        print(f"\n{'='*80}")
        print(f"USER: {query}")
        print(f"{'='*80}\n")
        
        result = copilot.process_query(query)
        print(result['response'])
        print("\n")
    
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using Cloud Security Copilot!")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            result = copilot.process_query(user_input)
            print(f"\nCopilot:\n{result['response']}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
