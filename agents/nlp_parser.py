import sys
import json

def parse_command(input_string):
    """
    Parses the input string into a command and its arguments.
    """
    parts = input_string.strip().split()
    if not parts:
        return {"command": None, "args": []}
    
    command = parts[0]
    args = parts[1:]
    
    return {"command": command, "args": args}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        parsed_result = parse_command(user_input)
        print(f"NLP PARSER: {json.dumps(parsed_result)}")
    else:
        # Handle case where no input is given
        print("NLP PARSER: No input received.")
