

def condition_delete_uuid(uuid):
    import shelve
    uuids_dat = 'uuids_dat.dat'
    uuid = str(uuid)
    db = shelve.open(uuids_dat,'c')
    try:
        db[uuid]
    except:
        db[uuid]=0
    if db[uuid] == 3:
        db[uuid]=0
        return True
    db[uuid] += 1
    return False
    