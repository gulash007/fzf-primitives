import clipboard
from thingies import shell_command
from thingies.git import extract_hash_from_log_line

from .core import DefaultPrompt, BasePrompt, mods
from .core import BasicLoop
from .core.FzfPrompt.options import Options
from .core.FzfPrompt.Prompt import Binding, PostProcessAction, PromptData, ServerCall
from .core.monitoring import Logger
import typer

app = typer.Typer()

# TODO: hotkey - copy commit message


def clip_author(prompt_data: PromptData):
    author = prompt_data.get_current_preview().split("Author: ", maxsplit=1)[1].split("\n", maxsplit=1)[0].strip()
    clipboard.copy(author)


def git_show(prompt_data: PromptData, selections: list[str]):
    # TODO: Replace with running GitShowPrompt with actions to change git show mode
    # TODO: Run the same mode as in GitLogPrompt preview
    try:
        pd = PromptData(
            choices=shell_command(
                [
                    "git",
                    "show",
                    "--color=always",
                    *[extract_hash_from_log_line(log_line) for log_line in selections],
                ]
            ).splitlines(),
            options=Options().ansi,
        )
        # pd.action_menu.add("ctrl-q", Binding("quit", PostProcessAction(mods.quit_app), end_prompt="abort"))
        DefaultPrompt.run(pd)
    except Exception as e:
        logger.exception(e)
    logger.debug("Git show ended")


# @mods.hotkey(HOTKEY.ctrl_c, 'echo "$(source ~/.zshforgit && extract_hash_from_log_line {})" | clip')
@mods.clip_output(extract_hash_from_log_line)
@mods.add_options(Options().ansi.multiselect)
@mods.preview("ctrl-6")(
    "git show",
    "source ~/.zshforgit && echo && hash=$(extract_hash_from_log_line {}) && git rev-list --count --first-parent $hash && git show --stat -p $hash --color=always",
    store_output=False,
)
@mods.preview("ctrl-f", main=True)(
    "git show fuller",
    "source ~/.zshforgit && echo && hash=$(extract_hash_from_log_line {}) && git rev-list --count --first-parent $hash && git show --pretty=fuller --stat -p $hash --color=always",
    store_output=False,
)
@mods.on_event("ctrl-y").run("clip author", ServerCall(clip_author))
@mods.on_event("ctrl-s").run("git show", ServerCall(git_show))
def run(prompt_data: PromptData, git_log_command: str = "git g --color=always --decorate --all"):
    prompt_data.choices = shell_command(git_log_command).splitlines()
    return DefaultPrompt.run(prompt_data)


@app.command()
def main():
    result = BasicLoop.run_once(lambda: run(PromptData()))
    if not result:
        logger.info("Exiting")
        return
    log_line = result[0]
    print(extract_hash_from_log_line(log_line))
    print(clipboard.paste())


if __name__ == "__main__":
    logger = Logger.get_logger()
    Logger.remove_handler("MAIN_LOG_FILE")
    Logger.remove_handler("STDERR")
    Logger.add_file_handler("FzGitLog")
    logger.enable("")
    app()
