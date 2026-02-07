# pr-doctor-agent

A tiny hello-world Python project with pytest and a GitHub Actions workflow that:

- runs tests on pushes to `main`
- on failure, runs an AI fixer that reads the test log + code, applies a patch, and opens a PR

## Local dev

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## GitHub Actions setup

Add these repository secrets:

- `OPENAI_API_KEY`: API key for the OpenAI API
- `OPENAI_MODEL` (optional): e.g. `gpt-5.2-codex`

`GITHUB_TOKEN` is provided automatically by GitHub Actions.

## Workflows

- `.github/workflows/tests.yml`: runs `pytest` on pushes to `main`
- `.github/workflows/auto-fix.yml`: when tests fail, downloads the test log and runs the AI fixer to create a PR

## Notes

The fixer script lives at `scripts/agent_fix.py`. It requests a unified diff from the model and applies it with `git apply`.
If the patch applies cleanly, it commits the change and opens a pull request.
