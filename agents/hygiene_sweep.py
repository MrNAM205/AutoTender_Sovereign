import sys
import json
import subprocess

def perform_hygiene(parsed_command):
    """
    Executes hygiene tasks based on the parsed command.
    """
    # It's possible the parsed_command is an empty string if the previous agent had no output
    if not parsed_command:
        return

    command = parsed_command.get("command")
    args = parsed_command.get("args", [])

    if command == "find":
        if not args:
            print("HYGIENE: 'find' command requires a search pattern.")
            return
        
        pattern = args[0]
        print(f"HYGIENE: Searching for files matching '{pattern}'...")
        
        try:
            # Using find . -name 'pattern' for safety and simplicity
            # We search from the current working directory '.'
            result = subprocess.run(['find', '.', '-name', pattern], capture_output=True, text=True, check=False)
            print("--- HYGIENE RESULTS ---")
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(f"HYGIENE (stderr): {result.stderr.strip()}")
            print("-----------------------")
        except FileNotFoundError:
            print("HYGIENE: 'find' command not found. Is it installed and in your PATH?")
        except Exception as e:
            print(f"HYGIENE: An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_input = " ".join(sys.argv[1:])
        
        # The nlp_parser prefixes its output, so we strip it.
        if raw_input.startswith("NLP PARSER: "):
            json_part = raw_input.replace("NLP PARSER: ", "", 1)
            try:
                parsed_json = json.loads(json_part)
                perform_hygiene(parsed_json)
            except json.JSONDecodeError:
                # This agent should only react to valid JSON from the parser.
                # If it's not valid, we silently do nothing.
                pass
