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
    server = prompt_data.server
    server.start()
    server.setup_finished.wait()
    executable_path = executable_path or "fzf"
    prompt_data.run_vars["executable_path"] = executable_path

    try:
        options = prompt_data.options
        logger.debug(
            "Running fzf with options",
            **{
                "trace_point": "running_fzf_with_final_options",
                "options": list(options),
                "str options": options.pretty(),
            },
        )
        # TODO: what happens if the output is too large?
        if entries_stream is None:
            exit_code = subprocess.run(
                [executable_path, *options],  # TODO: don't make options iterable; use method
                shell=False,
                input=prompt_data.fzf_input(),
                check=True,
                env=prompt_data.fzf_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
            ).returncode
        else:
            fzf_process = subprocess.Popen(
                [executable_path, *options],
                shell=False,
                stdin=subprocess.PIPE,  # ❗ this prevents reload actions from working
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=prompt_data.fzf_env,
                text=True,
                encoding="utf-8",
            )
            if (fzf_stdin := fzf_process.stdin) is None:
                raise FzfExecutionError("STDIN of fzf process is None")
            fzf_stdin.write(prompt_data.fzf_input())
            fzf_stdin.flush()

            def keep_piping():
                for entry in entries_stream:
                    # TODO: better name than line
                    item = prompt_data.converter(entry)
                    prompt_data.entries.append(entry)
                    try:
                        fzf_stdin.write(f"{item}{prompt_data.entries_delimiter}")
                        fzf_stdin.flush()
                    except Exception as e:
                        logger.exception(str(e), trace_point="error_writing_item_to_fzf_process")
                        prompt_data.entries.pop()
                        pass

            piping_thread = threading.Thread(target=keep_piping, daemon=True)
            piping_thread.start()
            fzf_process.wait()  # .communicate closes pipes leading to piping errors so wait for fzf to exit
            stdout, stderr = fzf_process.communicate()
            exit_code = fzf_process.returncode
            if exit_code != 0:
                raise subprocess.CalledProcessError(
                    returncode=exit_code, cmd=fzf_process.args, output=stdout, stderr=stderr
                )

    # TODO: use stdout and returncode?
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
        exit_code = err.returncode
    finally:
        server.should_close.set()
    server.join()
    if prompt_data.stage != "finished":
        logger.warning(
            "Prompt did not finish properly probably due to using base 'accept' or 'abort' actions and not PromptEndingAction. Result may be inaccurate.",
            trace_point="prompt_did_not_finish_properly",
            stage=prompt_data.stage,
        )
        end_status = "accept" if exit_code == 0 else "abort" if exit_code == 130 else None
        trigger = None
    else:
        if not (final_action := prompt_data.action_menu.bindings[prompt_data.trigger].final_action):
            err_message = "Prompt ended on trigger that doesn't have final action. How did we get here?"
            logger.error(
                err_message,
                **{"trace_point": "prompt_ended_on_trigger_without_final_action"},
            )
            raise RuntimeError(err_message)
        if final_action.post_processor:
            final_action.post_processor(prompt_data)
        end_status = final_action.end_status
        trigger = prompt_data.trigger
    return Result(
        end_status=end_status,
        trigger=trigger,
        entries=prompt_data.entries,
        query=prompt_data.query,
        current_index=prompt_data.current_index,
        selected_indices=prompt_data.selected_indices,
        selections=prompt_data.selections,
        target_indices=prompt_data.target_indices,
        obj=prompt_data.obj,
    )


class FzfExecutionError(Exception):
    pass
