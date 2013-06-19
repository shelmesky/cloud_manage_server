import httplib
import urllib
import time

from log import log
from settings import *


def http_client(url, data=None, method=None, data_type=None):
    logger = log(LOG_FILE)
    """
        http client for post and get data from remote server.
    """
    if not method: method = "POST"
    if not data_type: data_type = "application/json"

    headers = {"Agent":"cloud_manager","Accept":data_type}
    try:
        if data: data = urllib.urlencode(data)
        conn = httplib.HTTPConnection(HOST_CLOUD_MANAGER,port=PORT_CLOUD_MANAGER)
        if data:
            conn.request(method,url,body=data,headers=headers)
        else:
            conn.request(method,url,headers=headers)
        res = conn.getresponse()
    except Exception,e:
        logger.error("Error happend while connecting to server or send request!")
        logger.exception(e)
    else:
        status = res.status
        body = res.read()
        logger.info((body,time.ctime()))
        if status != 200:
            logger.debug('Post data to api server error: %d, data: %s' % (status,data))
        return body