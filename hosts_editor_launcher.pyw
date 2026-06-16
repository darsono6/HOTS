"""
Startup wrapper — place this file in the PARENT directory of the hosts_editor/ folder.
Run with: pythonw hosts_editor_launcher.pyw  (no console window)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hosts_editor.__main__ import main
main()
