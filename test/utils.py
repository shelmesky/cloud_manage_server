import shelve

def save_one_notification(content,content_type):
    db = shelve.open('one_notification.dat','c')
    if content == "notification":
        db[content['uuid']]['notification'] = content
    if content == "moniting":
        db[content[uuid]]['moniting'] = content
    db.close()


def get_on_notification(uuid):
    db = shelve.open('one_notification.dat','r')
    items = db.items()
    try:
        for i in items:
            ret = items[uuid]
        return ret
    except:
        return False