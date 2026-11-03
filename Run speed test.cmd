@echo off
rem Runs gpu_bench.py with the Python included in this folder. Nothing is installed.
cd /d "%~dp0"
"%~dp0python\python.exe" -B "%~dp0gpu_bench.py"
