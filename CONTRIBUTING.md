# Contributing

Use Python 3.9-compatible code and keep runtime dependencies minimal. Run `python3 -m unittest discover -s tests -v` before opening a pull request.

For model-facing changes, provide a small synthetic prompt, the macOS version, the `fm` command/options used, and the observed result. Mark mocked checks and live model checks separately. Never commit credentials, private prompts, transcripts, personal task data, signed binaries, or provisioning profiles.

Output validation and timeout/error handling are part of the public contract. Do not add silent cloud fallback or side effects to advisory jobs. Keep Paperclip publication opt-in.

The Apple executable is supplied by the operating system. Do not vendor it or Apple's model artifacts. Contributions to this repository are licensed under its MIT license.
