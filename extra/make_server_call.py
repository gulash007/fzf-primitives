from ..core.FzfPrompt.server.make_server_call import make_server_call, parse_args

if __name__ == "__main__":
    port, server_call_id, prompt_state, kwargs = parse_args()
    if response := make_server_call(port, server_call_id, prompt_state, **kwargs):
        print(response)
