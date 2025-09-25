import sys

def get_reflection(input_string):
    """
    Analyzes the input string for emotional keywords and returns a reflection.
    """
    # Convert to lowercase for case-insensitive matching
    lower_input = input_string.lower()

    # Define keyword mappings
    reflections = {
        "happy": "EMOTIONAL REFLECTOR: It sounds like you're feeling happy. I'm glad to hear that.",
        "joy": "EMOTIONAL REFLECTOR: That sounds joyful. Cherish this feeling.",
        "sad": "EMOTIONAL REFLECTOR: It sounds like you're feeling sad. I'm here to listen.",
        "angry": "EMOTIONAL REFLECTOR: It seems you're feeling angry. It's okay to feel that way.",
        "frustrated": "EMOTIONAL REFLECTOR: Frustration is a valid feeling. Let's work through it.",
        "confused": "EMOTIONAL REFLECTOR: It's okay to be confused. We can find clarity together.",
        "help": "EMOTIONAL REFLECTOR: It sounds like you're asking for help. I am here for you."
    }

    # Check for keywords
    for keyword, reflection in reflections.items():
        if keyword in lower_input:
            return reflection
            
    # No keyword found
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        reflection = get_reflection(user_input)
        if reflection:
            print(reflection)
