k#!/bin/bash
set +H  # ZSH-safe: disable history expansion

# === Sovereign Markdown Harvest Agent ===
# Scope: Harvest .md files from key folders, exclude venvs, rename with ascending clarity, inject semantic trace, and log provenance.

TARGET_DIR="$HOME/md_harvest"
mkdir -p "$TARGET_DIR"

FOLDERS=(
    "$HOME/Desktop"
    "$HOME/Downloads"
    "$HOME/sovereign"
)

declare -A name_count
counter=1
LOG="$TARGET_DIR/harvest_log.md"
echo "# Harvest Log - $(date)" > "$LOG"

for folder in "${FOLDERS[@]}"; do
    find "$folder" -type f -name "*.md" ! -path "*/venv/*" ! -path "*/.venv/*" 2>/dev/null | while read -r filepath; do
        base=$(basename "$filepath")
        count=${name_count["$base"]}

        if [[ -z "$count" ]]; then
            newname=$(printf "%03d_%s" "$counter" "$base")
            name_count["$base"]=1
        else
            newname=$(printf "%03d_%s_%d.%s" "$counter" "${base%.*}" "$count" "${base##*.}")
            name_count["$base"]=$((count + 1))
        fi

        cp "$filepath" "$TARGET_DIR/$newname"

        # Inject semantic trace
        echo "<!-- Source: $filepath -->" | cat - "$TARGET_DIR/$newname" > temp && mv temp "$TARGET_DIR/$newname"

        # Log provenance
        echo "- [$counter] '$filepath' → '$newname'" >> "$LOG"
        echo "[+] Harvested: $filepath → $newname"
        counter=$((counter + 1))
    done
done

echo "[✓] Harvest complete. Log saved to $LOG"

