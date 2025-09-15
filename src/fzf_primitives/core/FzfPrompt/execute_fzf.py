import subprocess
import threading
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .prompt_data import PromptData
from ..monitoring import Logger
from .prompt_data import PromptData, Result
from .shell import VerboseCalledProcessError

FZF_URL = "https://github.com/junegunn/fzf"
EXPECTED_FZF_ERR_CODES = (130, 1)  # 130 means aborted, 1 means accepted with no selection


# TODO: Allow propagation of exceptions through nested prompts (relevant for quit_app)
# ❗❗ FzfPrompt makes use of FZF_DEFAULT_OPTS variable
# Inspired by https://github.com/nk412/pyfzf
def execute_fzf[T, S](
    prompt_data: PromptData[T, S], *, executable_path=None, entries_stream: Iterable[T] | None = None
) -> Result[T, S]:
    logger = Logger.get_logger()
    try:
        prompt_data.run_initial_setup()
        server = prompt_data.server
        server.start()
        server.setup_finished.wait()
        executable_path = executable_path or "fzf"
        prompt_data.run_vars["executable_path"] = executable_path

        # TODO: catch 130 in mods.exit_round_on_no_selection (rename it appropriately)
        try:
            options = prompt_data.options
            logger.debug(
                "Running fzf with options",
                **{
                    "trace_point": "running_fzf_with_final_options",
                    "options": str(options),
                },
            )
            # TODO: what happens if the output is too large?
            delimiter = "\n" if "--read0" not in options else "\0"
            if entries_stream is None:
                subprocess.run(
                    [executable_path, *options],  # TODO: don't make options iterable; use method
                    shell=False,
                    input=prompt_data.fzf_input(delimiter),
                    check=True,
                    env=prompt_data.run_vars["env"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
            else:
                fzf_process = subprocess.Popen(
                    [executable_path, *options],
                    shell=False,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=prompt_data.run_vars["env"],
                    text=True,
                    encoding="utf-8",
                )
                if (fzf_stdin := fzf_process.stdin) is None:
                    raise FzfExecutionError("STDIN of fzf process is None")
                fzf_stdin.write(prompt_data.fzf_input(delimiter))
                fzf_stdin.flush()

                def keep_piping():
                    for entry in entries_stream:
                        # TODO: better name than line
                        line = prompt_data.converter(entry)
                        prompt_data.entries.append(entry)
                        try:
                            fzf_stdin.write(f"{line}{delimiter}")
                            fzf_stdin.flush()
                        except Exception as e:
                            logger.exception(str(e), trace_point="error_writing_line_to_fzf_process")
                            prompt_data.entries.pop()
                            pass

                piping_thread = threading.Thread(target=keep_piping, daemon=True)
                piping_thread.start()
                fzf_process.wait()  # .communicate closes pipes leading to piping errors so wait for fzf to exit
                stdout, stderr = fzf_process.communicate()
                if fzf_process.returncode != 0:
                    raise subprocess.CalledProcessError(
                        returncode=fzf_process.returncode, cmd=fzf_process.args, output=stdout, stderr=stderr
                    )

        except FileNotFoundError as err:
            if executable_path:
                raise FzfExecutionError(f"Error running 'fzf' with executable_path: {executable_path}") from err
            raise FzfExecutionError(
                f"Error running 'fzf' command. Are you sure it's installed and on PATH? ({FZF_URL})"
            ) from err
        except subprocess.CalledProcessError as err:
            if err.returncode not in EXPECTED_FZF_ERR_CODES:
                logger.exception(
                    stderr := err.stderr.strip(),
                    **{
                        "trace_point": "unexpected_fzf_called_process_error",
                        "err_code": err.returncode,
                        "stdout": err.stdout.strip(),
                        "stderr": stderr,
                    },
                )
                raise VerboseCalledProcessError(err)
        finally:
            server.should_close.set()
        server.join()
        if prompt_data.stage != "finished":
            # TODO: This may be explicitly allowed in the future (need to test when it's not)
            err_message = "Prompt not finished (you aborted prompt without finishing PromptData)"
            logger.error(err_message, **{"trace_point": "prompt_not_finished_properly"})
            raise RuntimeError(err_message)
        trigger = prompt_data.result.trigger
        if not (final_action := prompt_data.action_menu.bindings[trigger].final_action):
            err_message = "Prompt ended on trigger that doesn't have final action. How did we get here?"
            logger.error(
                err_message,
                **{"trace_point": "prompt_ended_on_trigger_without_final_action"},
            )
            raise RuntimeError(err_message)
        if final_action.post_processor:
            final_action.post_processor(prompt_data)
    finally:
        logger.info(
            "Applying post-processors",
            trace_point="applying_post_processors",
            count=str(len(prompt_data.post_processors)),
        )
        for post_processor in prompt_data.post_processors:
            post_processor(prompt_data)
    return prompt_data.result


class FzfExecutionError(Exception):
    pass
