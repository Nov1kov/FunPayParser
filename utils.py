# coding utf-8

def parseFloat(fstring):
    for s in fstring.split():
        try:
            return float(s)
        except ValueError:
            continue
    return 0


def parseInt(fint):
    result = ''
    for s in fint.split():
        try:
            int(s)
            result = result + s
        except ValueError:
            return int(result) if result != '' else ''
    return int(result) if result != '' else ''
