#!/bin/bash
# eval "$(winepath -u \"$@\")/audfprint/microphone_match.py"
eval "\"$(winepath -u "$@")/audfprint/microphone_match.py\""

# eval "\"${command}\""
# command="$(winepath -u "$@")/audfprint/microphone_match.py"
# eval "\"${command}\""
# read -p "Press Enter"
