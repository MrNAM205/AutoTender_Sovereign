#!/bin/bash
# This agent requests a tool call from the Gemini assistant.

# The 'if' condition prevents this from running on empty input
if [ -n "$1" ]; then
  echo "QNA_AGENT: Formulating a search request for the assistant..."
  # This special formatted string is a request for the Gemini model to call a tool.
  echo "GEMINI_TOOL_REQUEST: default_api.google_web_search(query='''$@''')"
fi
