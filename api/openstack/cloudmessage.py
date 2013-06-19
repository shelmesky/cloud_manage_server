from httpclient import HTTPClient
import settings


def send_sms(receivers, content):
    if isinstance(receivers, list):
        receivers = ','.join(receivers)
    
    try:
        content = content.encode('utf8')  # prepare for urlencode
    except:
        pass
    
    HTTPClient().post('%s/sms/send/' % settings.CLOUD_MESSAGE_HOST,
                      body={'receivers':receivers, 'content': content})

if __name__ == '__main__':
    send_sms('15317098900','hello python!')