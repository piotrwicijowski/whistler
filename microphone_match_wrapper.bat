@ECHO OFF
REM This is how the bash expression should look like in a standard .sh file:
REM eval "\"$(winepath -u "$@")/audfprint/microphone_match.py\""
REM however, due to the fact of multiple escapes
REM " is equivalent to \\\"
REM and \" is equivalent to \\\\\\\" (yes, that is seven backslashes)
SET "expression=eval \\\"\\\\\\\"$(winepath -u \\\"%cd%\\\")/audfprint/microphone_match.py\\\\\\\"\\\""
start /unix /usr/bin/xterm -e bash -c "%expression%"
