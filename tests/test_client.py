import subprocess
import unittest
from unittest.mock import patch
from apple_fm_tools import client


class ClientTests(unittest.TestCase):
    def test_prompt_is_not_shell_code_or_cli_option(self):
        prompt = '--tool ocr; $(touch /tmp/nope)'
        with patch.object(client.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'ok\n', '')) as run:
            self.assertEqual(client.respond(prompt), 'ok')
        argv = run.call_args.args[0]
        self.assertEqual(argv[-2:], ['--text', prompt])
        self.assertNotIn('shell', run.call_args.kwargs)

    def test_timeout_is_an_actionable_error(self):
        with patch.object(client.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fm', 1)):
            with self.assertRaisesRegex(client.FMError, 'timeout'):
                client.respond('hello', timeout=1)

    def test_missing_cli_is_an_actionable_error(self):
        with patch.object(client.subprocess, 'run', side_effect=FileNotFoundError):
            with self.assertRaisesRegex(client.FMError, 'not found'):
                client.available()

    def test_nonzero_exit_not_returned_as_answer(self):
        with patch.object(client.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'license required')):
            with self.assertRaisesRegex(client.FMError, 'license required'):
                client.respond('hello')

    def test_count_includes_requested_instructions(self):
        with patch.object(client.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '12', '')) as run:
            self.assertEqual(client.count_tokens('hello', instructions='be brief'), 12)
        self.assertEqual(run.call_args.args[0][-4:], ['--instructions', 'be brief', '--text', 'hello'])

if __name__ == '__main__':
    unittest.main()
