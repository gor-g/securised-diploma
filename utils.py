
def fread(file: str):
    with open(file, "r") as f:
        content = f.read()
    return content