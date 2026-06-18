# Local UI

This package contains the browser-based interface for the ontology pipeline.

## Launch

From the repository root, start the UI with either of these commands:

```bash
eu-ai-act-ontology --ui
```

```bash
python src/main.py --ui
```

The server binds to `127.0.0.1` on an automatically chosen local port and opens the page in your default browser.

## What it does

The UI is a lightweight local control surface for:

- selecting pipeline goals
- editing input and output paths
- adjusting concept and chapter limits
- watching live progress and run logs
- reviewing the structured pipeline report after completion

The page is rendered directly by `src/presentation/web_ui.py`; there is no separate frontend build step.

## Notes

- Keep the Python process running while the UI is open.
- Repository-relative paths are resolved against the project root.
- LLM-backed stages still depend on valid settings in `config/api_configs.json`.