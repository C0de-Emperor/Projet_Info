def GetAppConfig() -> dict:
    with open("config.txt") as f:
        txt = f.read()

    preParam = txt.split("\n")
    for i in range(len(preParam)):
        preParam[i]=preParam[i].replace(" ", "")

    parameters = dict([ preParam[i].split(':') for i in range(preParam.__len__()) ])
    return parameters
    