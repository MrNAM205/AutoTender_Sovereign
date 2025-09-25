#!/bin/bash
source ovb_registry.sh

while true; do
  echo "🧠 OVB Listening..."
  read -p "Input: " user_input

  # Always run emotional reflection on the raw input
  call_agent "emotional_reflector" "$user_input"

  # Parse the command to get structured JSON
  parsed_input_json=$(call_agent "nlp_parser" "$user_input")
  echo "$parsed_input_json" # Show the parsed output for clarity

  # Extract command from JSON for routing.
  # This uses grep and cut to avoid dependencies like jq.
  command=$(echo "$parsed_input_json" | grep -o '"command": *"[^"]*"' | cut -d'"' -f4)

  # Route based on the extracted command
  case "$command" in
    "find")
      call_agent "hygiene_sweep" "$parsed_input_json"
      ;;
    "ingest")
      call_agent "payload_ingest" "$parsed_input_json"
      ;;
    *)
      # If no specific agent handles the command, treat it as a general query.
      # We pass the original, full user input to the Q&A agent.
      if [ -n "$user_input" ]; then # Only call if there was input
          call_agent "qna_agent" "$user_input"
      fi
      ;;
  esac

  echo "🔁 Loop complete. Awaiting next input..."
done