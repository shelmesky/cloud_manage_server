'''
Client tools for HTTP calls. It will raise HTTP exceptions according to the exceptions from API calls.
'''
import socket
import httplib2
import logging
from urllib import urlencode
from xml.etree.ElementTree import fromstring as str_to_xml_tree

try:
    import json
except ImportError:
    import simplejson as json

import exceptions

logfile = 'sendsms.log'
CLOUD_MESSAGE_HOST = 'http://172.16.0.162:8088'

class ClientException(Exception):
    """
    The base exception class for all exceptions this library raises.
    """
    def __init__(self, code, message=None, details=None):
        self.code = code
        self.message = message or self.__class__.message
        self.details = details

    def __str__(self):
        return '%s (HTTP %s)' % (self.message, self.code)


class BadRequest(ClientException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    message = 'Bad request'


class Unauthorized(ClientException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    message = 'Unauthorized'


class Forbidden(ClientException):
    """
    HTTP 403 - Forbidden: your credentials don't give you access to this
    resource.
    """
    http_status = 403
    message = 'Forbidden'


class NotFound(ClientException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = 'Not found'


class OverLimit(ClientException):
    """
    HTTP 413 - Over limit: you're over the API limits for this time period.
    """
    http_status = 413
    message = 'Over limit'


class HTTPNotImplemented(ClientException):
    """
    HTTP 501 - Not Implemented: the server does not support this operation.
    """
    http_status = 501
    message = 'Not Implemented'


class SeverError(ClientException):
    """
    HTTP 500 - ServerError
    """
    http_status = 500
    message = 'Server Error'


CODE_MAP = dict((c.http_status, c) for c in [BadRequest, Unauthorized,
                   Forbidden, NotFound, OverLimit, HTTPNotImplemented])


def from_response(response, body):
    """
    Return an instance of an ClientException or subclass
    based on an httplib2 response.

    Usage::

        resp, body = http.request(...)
        if resp.status != 200:
            raise exception_from_response(resp, body)
    """
    cls = CODE_MAP.get(response.status, ClientException)
    if body:
        message = 'n/a'
        details = 'n/a'
        if hasattr(body, 'keys'):
            error = body[body.keys()[0]]
            message = error.get('message', None)
            details = error.get('details', None)
        return cls(code=response.status, message=message, details=details)
    else:
        return cls(code=response.status)


def initlog():       
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = initlog()

class HTTPClient(httplib2.Http):
    USER_AGENT = 'CLOUD-OPEN'
    
    def __init__(self, insecure=False, timeout=None, accept='application/json',
                 content_type='application/x-www-form-urlencoded', encoding='utf-8'):
        
        #accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
        # content_type: application/json; charset=utf-8
        
        super(HTTPClient, self).__init__(timeout=timeout)
        
        self.encoding = encoding
        self.content_type = content_type
        self.accept = accept
    
        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

    
    def _extra_body(self, content_type, body):
        if '/xml' in content_type:
            try:
                return str_to_xml_tree(body)
            except ValueError:
                LOG.debug('can not extra body as XML ElementTree: %s', body)
                
        if '/json' in content_type:
            try:
                return json.loads(body)
            except ValueError:
                LOG.debug('can not dump body as JSON: %s', body)
                
        return body  # nothing changed
    
    
    def request(self, *args, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = self.accept
        kwargs['headers']['Accept-Charset'] = self.encoding
        
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = self.content_type
            if '/json' in self.content_type:
                kwargs['body'] = json.dumps(kwargs['body'])  # the server side needs to call json.loads
            else:
                kwargs['body'] = urlencode(kwargs['body'])  # this is for most case, such as a form post

        LOG.debug('sending request: %s || %s' % (args, kwargs))

        resp, body = super(HTTPClient, self).request(*args, **kwargs)
        print resp

        content_type = resp.get('content-type')  # may not be the same as ['headers']['Accept']
        if body and content_type:
            body = self._extra_body(content_type, body)
        
        LOG.debug("Got body: %s" % body)

        #if resp.status in (400, 401, 403, 404, 408, 409, 413, 500, 501):
        #    raise from_response(resp, body)

        return resp, body

    
    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)


    def post(self, url, **kwargs):
        return self.request(url, 'POST', **kwargs)


def send_sms(receivers, content):
    if isinstance(receivers, list):
        receivers = ','.join(receivers)
        
    try:
        content = content.encode('utf8')  # prepare for urlencode
    except:
        pass
    
    HTTPClient(3).post('%s/sms/send/' % CLOUD_MESSAGE_HOST,
                      body={'receivers':receivers, 'content': content})

if __name__ == '__main__':
    send_sms('15317098900','hello python!')

