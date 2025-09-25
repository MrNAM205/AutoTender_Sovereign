import sys
import json
import urllib.request

def ingest_payload(parsed_command):
    """
    Executes ingestion tasks based on the parsed command.
    """
    if not parsed_command:
        return

    command = parsed_command.get("command")
    args = parsed_command.get("args", [])

    if command == "ingest":
        if not args:
            print("PAYLOAD INGEST: 'ingest' command requires a URL.")
            return
        
        url = args[0]
        # Basic validation to ensure it looks like a URL
        if not url.startswith(('http://', 'https://')):
            print(f"PAYLOAD INGEST: Invalid URL format: {url}")
            return

        print(f"PAYLOAD INGEST: Ingesting from '{url}'...")
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                # Check if the request was successful
                if 200 <= response.status < 300:
                    content_type = response.headers.get('Content-Type', '')
                    # Read a limited amount to avoid printing huge files
                    content = response.read(4096).decode('utf-8', errors='ignore')
                    
                    print("--- PAYLOAD SUMMARY ---")
                    print(f"Status: {response.status}")
                    print(f"Content-Type: {content_type}")
                    print(f"Content (first 4KB):\n{content[:1024]}...") # Print first 1KB of the 4KB read
                    print("-----------------------")
                else:
                    print(f"PAYLOAD INGEST: Failed to retrieve content. Status code: {response.status}")

        except Exception as e:
            print(f"PAYLOAD INGEST: An error occurred during ingestion: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_input = " ".join(sys.argv[1:])
        
        # The nlp_parser prefixes its output, so we strip it.
        if raw_input.startswith("NLP PARSER: "):
            json_part = raw_input.replace("NLP PARSER: ", "", 1)
            try:
                parsed_json = json.loads(json_part)
                ingest_payload(parsed_json)
            except json.JSONDecodeError:
                # Silently do nothing if the JSON is malformed.
                pass
