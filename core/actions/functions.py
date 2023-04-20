from typing import Optional


def preview_basic(query: str, selections: list[str]):
    sep = "\n\t"
    # if indices:
    #     selections = [f"{index}\t{selection}" for index, selection in zip(indices, selections)]
    return f"query: {query}\nselections:\n\t{sep.join(selections)}"
