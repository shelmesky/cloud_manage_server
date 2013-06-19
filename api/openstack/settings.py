from hashlib import sha224

OPENSTACK_HOST = '172.16.0.31'
OPENSTACK_KEYSTONE_URL = 'http://%s:5000/v2.0' % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = 'members'

# TODO: Encryption service token
# user this to fake admin token, for user maintenance
SERVICE_ENDPOINT = 'http://%s:35357/v2.0' % OPENSTACK_HOST
SERVICE_TOKEN = 'openstack'

## for billing
#ADMIN_USER_NAME = 'admin'
#ADMIN_PASSWORD = 'openstack'
##ADMIN_PASSWORD = 'C1oud-open'
#ADMIN_TENANT = 'admin'


ADMIN_USER_NAME = 'test1@test.com'
ADMIN_PASSWORD = sha224('_!@$#&^_%s' % (1)).hexdigest()[:10]
ADMIN_TENANT = 'admin'

POWER_STATES = {
    0: "NO STATE",
    1: "RUNNING",
    2: "BLOCKED",
    3: "PAUSED",
    4: "SHUTDOWN",
    5: "SHUTOFF",
    6: "CRASHED",
    7: "SUSPENDED",
    8: "FAILED",
    9: "BUILDING",
}

PAUSE = 0
UNPAUSE = 1
SUSPEND = 0
RESUME = 1

# status from nova server
INSTANCE_STATUS_ACTIVE = 'ACTIVE'

FINAL_STATUS = ('ACTIVE', 'ERROR', 'SUSPENDED', 'DELETED', 'SHUTOFF')


CLOUD_MESSAGE_HOST = 'http://172.16.0.207:8088'
