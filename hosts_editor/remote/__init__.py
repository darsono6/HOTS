"""Remote administration agent for HOTS Hosts.

The agent runs in the background as SYSTEM (scheduled task), opens an outbound HTTPS
connection to the HOTS web console and executes a fixed whitelist of actions
(see ``actions.py``). It never runs arbitrary commands sent by the server.
"""

AGENT_VERSION = "1.0.0"
PROTOCOL_VERSION = 1
AGENT_EXE_NAME = "HOTS Remote Agent.exe"
TASK_NAME = "HOTS Hosts Remote Agent"
