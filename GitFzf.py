if __name__ == "__main__":
    __package__ = "fzf_primitives"
from .core.BasicLoop import BasicRecursiveLoop
from .core.options import HOTKEY, Options
from .core.ActionMenu import ActionMenu
from .core.Prompt import Prompt
from .core.MyFzfPrompt import run_fzf_prompt
from git.cmd import Git
from git.repo import Repo

repo = Repo("/Users/honza/Documents/Projects/PythonPackages/fzf_primitives")
cmd = Git("/Users/honza/Documents/Projects/PythonPackages/fzf_primitives")


# GitGraph -> branch selection + actions + preview `git log branch`

class GitCommitPrompt(Prompt):
    pass

class GitLogPrompt(Prompt):
    _instance_created = False

    def __call__(self):
        return self.git_log()

    @Options().ansi
    def git_log(self, *, options: Options = Options()):
        log_lines = cmd.log("--oneline", "--graph", "--decorate", "--all", "--color=always").splitlines()
        return run_fzf_prompt(log_lines, self._options + options)

class GitFzf:
    def run(self):
        pass

import re

# No need to worry about conflicts since git log outputs more characters in short hash when there are conflicts
# outputting hash (and not something in message is guaranteed by outputting the first one)
hash_regex = re.compile(r"(^|\s)(\w{7,8})\s")


def extract_short_hash(log_line: str):
    return hash_regex.search(log_line).group(2)


if __name__ == "__main__":
    g = GitLogPrompt()
    b = BasicRecursiveLoop(g)

    # no multiselect
    log_line = b.run()[0]
    short_hash = extract_short_hash(log_line)
    res = GitCommitPrompt(short_hash)()

    log_lines = b.run()
    # short_hashes = [extract_short_hash(line) for line in log_lines]
    # print(cmd.show(, "--color=always"))

    # print(short_hashes)
