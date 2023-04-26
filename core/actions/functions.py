def preview_basic(query: str, selection: str, selections: list[str]):
    sep = "\n\t"
    # if indices:
    #     selections = [f"{index}\t{selection}" for index, selection in zip(indices, selections)]
    return f"query: {query}\nselection: {selection}\nselections:\n\t{sep.join(selections)}"
