import argparse
import subprocess
import sys
import os

# Add the AutoTender_Sovereign directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'AutoTender_Sovereign'))

try:
    import clause_scanner
except ImportError:
    print("Error: Could not import the clause_scanner module.")
    print("Please ensure the script is run from the project root directory and that clause_scanner.py is in the AutoTender_Sovereign directory.")
    sys.exit(1)

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
    found_keywords = clause_scanner.main(args.document, keywords_to_scan)
    
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
    remedy_script_path = os.path.join(os.path.dirname(__file__), 'AutoTender_Sovereign', 'remedy_generator.py')
    python_executable = os.path.join(os.path.dirname(__file__), 'AutoTender_Sovereign', 'venv', 'bin', 'python3')

    command = [
        python_executable,
        remedy_script_path,
        "--violation", violation
    ]
    
    # Add user/creditor info if provided
    if args.user_name: command.extend(["--user-name", args.user_name])
    if args.user_address: command.extend(["--user-address", args.user_address])
    if args.creditor_name: command.extend(["--creditor-name", args.creditor_name])
    if args.creditor_address: command.extend(["--creditor-address", args.creditor_address])
    command.extend(["--bill-file-name", os.path.basename(args.document)])

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print(f"Error: Could not find the Python interpreter at {python_executable}")
        print("Please ensure the virtual environment is set up correctly.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the remedy generator: {e}")

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