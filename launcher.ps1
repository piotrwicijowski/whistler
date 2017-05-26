$date = Get-Date -format "yyyyMMdd_HHmmss"
pythonw.exe program\microphone_match_gui.py > $($date)+'_log.txt' 2> $($date)+'_error.txt'
