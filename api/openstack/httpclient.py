'''
Client tools for HTTP calls. It will raise HTTP exceptions according to the exceptions from API calls.
'''
import httplib2
from urllib import urlencode
from xml.etree.ElementTree import fromstring as str_to_xml_tree

try:
    import json
except ImportError:
    import simplejson as json

from LOGGER import logger as LOG

import exceptions


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
        
        content_type = resp.get('content-type')  # may not be the same as ['headers']['Accept']
        if body and content_type:
            body = self._extra_body(content_type, body)

        if resp.status in (400, 401, 403, 404, 408, 409, 413, 500, 501):
            raise exceptions.from_response(resp, body)

        return resp, body

    
    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)


    def post(self, url, **kwargs):
        return self.request(url, 'POST', **kwargs)
    