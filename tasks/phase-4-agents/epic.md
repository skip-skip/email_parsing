# Epic 4 — Email Intake & Parsing Agents

## Goal
Build the agents that receive raw emails, extract structured task information using the local LLM, and persist parsed results.

## Status
Not Started

## Tasks
| Task | Title | Status | Dependencies |
|------|-------|--------|-------------|
| 4.1 | Set Up Ollama Client Service | Complete | 1.1 |
| 4.2 | Create Prompt Templates | Complete | None |
| 4.3 | Build Email Intake Agent | Complete | 2.2, 2.6, 3.4 |
| 4.4 | Build Email Parsing Agent | Not Started | 4.1, 4.2, 2.6 |
| 4.5 | Build Conversation Tracker | Not Started | 4.4, 2.6 |
| 4.6 | Agent Integration Tests | Not Started | 4.3–4.5 |

## Acceptance Criteria
- Ollama client connects and generates responses
- Prompts produce valid JSON
- Intake agent stores emails and detects duplicates
- Parsing agent extracts structured fields with confidence scores
- Conversation tracker merges reply information correctly
