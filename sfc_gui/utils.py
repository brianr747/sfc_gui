

def sort_series(serlist):
    serlist.sort()
    if 't' in serlist:
        serlist.remove('t')
        serlist.insert(0, 't')
    if 'k' in serlist:
        serlist.remove('k')
        serlist.insert(0,'k')
    return serlist