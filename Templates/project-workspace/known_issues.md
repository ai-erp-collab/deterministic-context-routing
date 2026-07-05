# Known Issues

Keep this file short. Add recurring workspace problems only when future agents
need a required handling rule.

## Encoding Or File Format Risk

- **Symptom:** Important text or source artifacts appear corrupted, unreadable, or unexpectedly reformatted.
- **Cause:** The file was read or rewritten with the wrong encoding or tool.
- **Required handling:** Inspect encoding and file format before changing the file. Preserve the project's declared encoding and record any recovery.

## Session State Overread

- **Symptom:** An agent treats old session history as current instruction.
- **Cause:** The agent read past the latest `<!-- AGENT-SESSION-STOP -->` marker.
- **Required handling:** Read only the latest session entry by default. Treat older entries as history, not current instruction.
