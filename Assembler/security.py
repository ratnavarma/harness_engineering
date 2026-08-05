"""Day 2: a small policy gate for tool execution.

Concept: separate an action's capability from the decision to permit it.
Design rules: always deny catastrophic shell commands, make read access simple,
and require explicit human approval for safe-mode writes and commands.
"""

import re

READ_TOOLS = {"read_file", "list_files", "grep"}
# These patterns protect the host even when a caller deliberately selects yolo.
DENY_PATTERNS = (
    # Recursive forced deletion may never target a filesystem root or home.
    r"\brm\s+(?:(?:-[A-Za-z]*[rf][A-Za-z]*|--recursive|--force)\s+)+(?:/|~|\$HOME)(?:/|\s|$)",
    # Privilege escalation changes the harness's intended blast radius.
    r"\bsudo\b",
    # Filesystem formatting and image writes are not recoverable tool actions.
    r"\b(?:mkfs(?:\.\w+)?|dd\s+if=)",
    # A downloaded shell script has no inspectable approval boundary.
    r"\bcurl\b[^|\n]*\|\s*(?:ba)?sh\b",
    # Forced remote history changes require a separate, intentional workflow.
    r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?|-f)\b",
    # Disk-device redirection can overwrite a whole physical volume.
    r">>\s*/dev/sd[a-z]\b|>\s*/dev/sd[a-z]\b",
)


class Policy:
    """Decide whether one neutral tool call may execute.

    Calls use the loop's neutral `{"name", "args"}` shape, so a policy can
    remain independent of individual tool implementations.
    """

    def __init__(self, mode: str = "safe", approver=None) -> None:
        """Create a read-only, safe, or unrestricted policy."""
        if mode not in {"read-only", "safe", "yolo"}:
            raise ValueError("mode must be 'read-only', 'safe', or 'yolo'")
        self.mode = mode
        self.approver = approver or (lambda call, reason: False)

    def check(self, call: dict) -> str | None:
        """Allow a call with None, or return the reason that blocks it.

        Always-deny checks intentionally happen before mode selection: yolo is
        convenient for a demo, not permission to run an irreversible command.
        """
        name = call["name"]
        command = str(call.get("args", {}).get("command", ""))
        if name == "bash" and any(re.search(pattern, command, re.IGNORECASE) for pattern in DENY_PATTERNS):
            return "command violates the always-deny safety policy"
        if name in READ_TOOLS or self.mode == "yolo":
            return None
        if self.mode == "read-only":
            return "read-only mode permits only read tools"
        if not self.approver(call, "safe mode requires approval"):
            return "approval was not granted"
        return None
