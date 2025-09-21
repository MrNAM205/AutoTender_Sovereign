import argparse
import sys
import os

from autotender import scanner, generator

# Define the mapping between keywords and violation types
KEYWORD_TO_VIOLATION = {
    "not a negotiable instrument": "denial_of_negotiability",
    "tender refused": "dishonor_of_tender",
    # Add more mappings here
}

def main(args):
    print(f"--- Starting Sovereign Cockpit for document: {args.document} ---")
    
    # 1. Scan the document for contradiction clauses
    print("\n--- Scanning for contradiction clauses... ---")
    keywords_to_scan = list(KEYWORD_TO_VIOLATION.keys())
    found_keywords = scanner.scan(args.document, keywords_to_scan)
    
    if not found_keywords:
        print("No contradiction clauses found. No further action taken.")
        # Even if no contradictions, we might want to generate a standard tender letter
        print("\n--- No contradictions found, proceeding with standard tender letter generation. ---")
        violation = "tender_letter"
    else:
        print(f"\nFound the following contradictions: {', '.join(found_keywords)}")
        # For now, we'll just generate remedies for the found contradictions.
        # A more advanced logic could decide which remedy to prioritize.
        violation = KEYWORD_TO_VIOLATION.get(found_keywords[0]) # Just take the first one for now

    # 2. Generate remedy
    print(f"\n--- Generating remedy for violation: '{violation}' ---")
    
    try:
        generator.generate(
            violation=violation,
            user_name=args.user_name,
            user_address=args.user_address,
            creditor_name=args.creditor_name,
            creditor_address=args.creditor_address,
            bill_file_name=os.path.basename(args.document)
        )
    except ValueError as e:
        print(f"Error generating remedy: {e}")

    print("\n--- Sovereign Cockpit process complete. ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sovereign Financial Cockpit: Automate document scanning and remedy generation.")
    parser.add_argument("--document", required=True, help="Path to the document to process.")
    parser.add_argument("--user-name", help="Your name.")
    parser.add_argument("--user-address", help="Your address.")
    parser.add_argument("--creditor-name", help="Creditor's name.")
    parser.add_argument("--creditor-address", help="Creditor's address.")
    
    args = parser.parse_args()
    
    main(args)