import json

def obtain_token() -> str:
    if obtain_token.token is None:
        with open('bot/config.json') as f:
            data = json.load(f)
            print(data)
            obtain_token.token = data["token"]

    return obtain_token.token

obtain_token.token = None