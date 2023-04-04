# fzf-primitives

## Prompt

- to complete a prompt:
  - give it its `._instance_created = False` class attribute (for the singleton pattern)
  - define `.run` method and decorate it. `.run` is only supposed to be called with keyworded `options` argument
