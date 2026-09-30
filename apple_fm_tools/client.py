"""Small subprocess API for Apple's on-device fm CLI."""
import subprocess
from pathlib import Path


class FMError(RuntimeError):
    """The local CLI is unavailable, timed out, or rejected a request."""


def execute(argv, *, timeout=90):
    try:
        result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise FMError("Apple's fm CLI was not found. This project requires macOS with /usr/bin/fm.") from exc
    except subprocess.TimeoutExpired as exc:
        raise FMError(f"fm exceeded the {timeout}-second timeout") from exc
    if result.returncode:
        raise FMError((result.stderr or result.stdout or f"fm exited with status {result.returncode}").strip()[:1200])
    return result.stdout.strip()


def respond(prompt, *, instructions=None, image=None, schema=None, timeout=90):
    """Return text (or schema-constrained JSON text) from one independent request.

    schema is Apple's generated schema JSON, not an arbitrary JSON Schema dialect.
    No conversation state is retained by this wrapper.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise FMError("A nonempty text prompt is required")
    argv = ['/usr/bin/fm', 'respond', '--model', 'system', '--no-stream', '--greedy']
    if instructions is not None:
        argv += ['--instructions', instructions]
    if image is not None:
        argv += ['--image', str(Path(image).expanduser().resolve(strict=True))]
    if schema is not None:
        argv += ['--schema', schema]
    # Explicit --text prevents prompt text beginning with '-' becoming CLI options.
    argv += ['--text', prompt]
    return execute(argv, timeout=timeout)


def count_tokens(prompt, *, instructions=None, timeout=30):
    """Count text tokens; this is not output usage or total inference accounting."""
    argv = ['/usr/bin/fm', 'count-tokens', '--quiet']
    if instructions is not None:
        argv += ['--instructions', instructions]
    argv += ['--text', prompt]
    return int(execute(argv, timeout=timeout))


def available():
    """Return fm's availability description; unavailable CLI failures raise FMError."""
    return execute(['/usr/bin/fm', 'available'], timeout=30)
