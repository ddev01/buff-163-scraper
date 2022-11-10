def cookieFormatter(cookieString):
    cookieString = cookieString.replace('=', ':').replace(';', 'x@A').replace(' ', '')
    cookieString = cookieString.split('x@A')
    cookieDict = {}
    for item in cookieString:
        temp = item.split(":")
        cookieDict[temp[0]] = temp[1]
    return cookieDict