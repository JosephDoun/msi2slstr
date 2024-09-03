from os.path import split



class ProductName:
    def __init__(self, sen2name: str, sen3name: str) -> None:
        self.sen2name = split(sen2name)[-1]
        self.sen3name = split(sen3name)[-1]

    def __str__(self) -> str:
        pass
