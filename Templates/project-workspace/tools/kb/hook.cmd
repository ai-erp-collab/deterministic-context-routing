@echo off
rem Windows hook launcher: runs kb.py with the first Python >= 3.9 among python, python3, py.
rem Store stubs and older interpreters fail the probe; no usable Python = silent exit 0.
for %%p in (python python3 py) do (
  %%p -c "import sys;sys.exit(sys.version_info<(3,9))" >nul 2>&1 && (
    %%p "%~dp0kb.py" hook %1
    exit /b 0
  )
)
exit /b 0
