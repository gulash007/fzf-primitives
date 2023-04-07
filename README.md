# fzf-primitives

## Prompt

- to complete a prompt:
  - give it its `._instance_created = False` class attribute (for the singleton pattern)
  - define `.run` method and decorate it. `.run` is only supposed to be called with keyworded `options` argument

## ActionMenu

- Adding new actions requires creating a function in its own file in "core/actions/" folder and turning it into a command.
  - This involves:
    - using a decorator to create a printing wrapper (shouldn't use @ syntax but rather assign a new function)
    - using typer to create the CLI and registering the printing function
  - Turning them into commands has the benefit of being used in fzf prompt without leaving it (no need to perform the action upon leaving prompt and interpreting a --expect hotkey).

## Previews

- Actions-turned-commands serve as convenient previews
