import os
import subprocess
import textwrap
from pathlib import Path

from openai import OpenAI, RateLimitError


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "pytest-output.txt"


def read_repo_files() -> str:
    allowed_prefixes = ("tests/", "hello.py")
    files = []
    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    for path in tracked:
        if not path.startswith(allowed_prefixes):
            continue
        full_path = ROOT / path
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception:
            continue
        files.append(f"\n--- {path} ---\n{content}")
    return "\n".join(files)


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required.")
        return 1

    model = os.getenv("OPENAI_MODEL", "gpt-5.2-codex")

    if not LOG_PATH.exists():
        print(f"Missing test log: {LOG_PATH}")
        return 1

    test_log = LOG_PATH.read_text(encoding="utf-8")
    repo_files = read_repo_files()

    if not repo_files.strip():
        print("No repo files found to analyze.")
        return 1

    prompt = textwrap.dedent(
        f"""
        You are a code-fixing agent.
        You are given failing pytest output and the project files.
        Produce a unified diff in git format (must start with "diff --git").
        Only output the diff. Do not include any explanations or other text.

        Pytest output:
        {test_log}

        Project files:
        {repo_files}
        """
    ).strip()

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=model,
            input=prompt,
        )
    except RateLimitError as exc:
        message = str(exc)
        if "insufficient_quota" in message:
            print(
                "OpenAI API quota exceeded. Enable billing or add credits on the API platform, "
                "then re-run this workflow."
            )
            return 1
        print(f"OpenAI rate limit error: {message}")
        return 1

    diff = response.output_text.strip()
    if not diff.startswith("diff --git"):
        print("Model did not return a git diff.")
        print(diff)
        return 1

    patch_path = ROOT / "ai-fix.patch"
    patch_path.write_text(diff, encoding="utf-8")

    try:
        subprocess.run(["git", "apply", str(patch_path)], check=True)
    except subprocess.CalledProcessError:
        print("Failed to apply patch.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
