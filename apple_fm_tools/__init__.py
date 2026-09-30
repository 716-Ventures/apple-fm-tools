"""Utilities for Apple's on-device Foundation Model via fm."""
from .client import FMError, available, count_tokens, respond
from .worker import run_job

__all__ = ['FMError', 'available', 'count_tokens', 'respond', 'run_job']
