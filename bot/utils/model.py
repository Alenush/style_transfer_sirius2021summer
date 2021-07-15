class Model:
    def __init__(self, model_name) -> None:
        pass

    def get_reply(self, text) -> str:
        return "Reply"


def load_models(names: dict) -> dict[Model]:
    mds = dict()
    for name, model_name in names.items():
        mds[name] = Model(model_name)

    return mds
