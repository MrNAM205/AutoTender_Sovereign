# ovb_registry.sh
declare -A OVB_AGENTS=(
  ["nlp_parser"]="agents/nlp_parser.sh"
  ["hygiene_sweep"]="agents/hygiene_sweep.sh"
  ["payload_ingest"]="agents/payload_ingest.sh"
  ["emotional_reflector"]="agents/emotion_reflector.sh"
  ["qna_agent"]="agents/qna_agent.sh"
)

function call_agent() {
  local agent="$1"
  shift
  if [[ -n "${OVB_AGENTS[$agent]}" ]]; then
    bash "${OVB_AGENTS[$agent]}" "$@"
  else
    echo "Agent '$agent' not found in registry."
  fi
}
