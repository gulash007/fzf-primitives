import shlex
import subprocess
import tempfile
from pathlib import Path


class VerboseCalledProcessError(subprocess.CalledProcessError):
    def __init__(self, err: subprocess.CalledProcessError) -> None:
        super().__init__(err.returncode, err.cmd, err.output, err.stderr)

    def __str__(self) -> str:
        stderr = self.stderr.decode() if isinstance(self.stderr, bytes) else str(self.stderr)
        return f"{super().__str__()}\n{stderr.strip()}"


def shell_command(
    command: list[str] | str,
    executable: str | None = "bash",
    shell: bool = True,
    input_: str | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    blocking: bool = False,
    cwd: str | Path | None = None,
) -> str:
    if not shell:
        if isinstance(command, str):
            command = shlex.split(command)
        executable = None
    elif isinstance(command, list):
        command = shlex.join(command)
    try:
        if not blocking:
            output = subprocess.run(
                command,
                executable=executable,
                shell=shell,
                check=True,
                capture_output=True,
                input=input_.encode() if input_ else None,
                env=env,
                timeout=timeout,
                cwd=cwd,
            )
            return output.stdout.decode()
        else:
            with tempfile.NamedTemporaryFile(mode="r") as temp_file:
                subprocess.run(
                    command,
                    executable=executable,
                    shell=shell,
                    check=True,
                    capture_output=False,
                    input=input_.encode() if input_ else None,
                    env=env,
                    timeout=timeout,
                    stdout=temp_file,
                    cwd=cwd,
                )
                with open(temp_file.name, "r") as f:
                    return f.read()
    except subprocess.CalledProcessError as e:
        raise VerboseCalledProcessError(e) from None
