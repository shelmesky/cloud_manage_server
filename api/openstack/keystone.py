import settings

from keystoneclient.v2_0 import client as keystone_client
from keystoneclient.v2_0 import tokens

#from common.api.utils import url_for
import LOG


def _keystoneclient(username=None, password=None, endpoint=None,
                    tenant_id=None, token_id=None, auth_url=None):
    
    c = keystone_client.Client(username=username, 
                               password=password,
                               token=token_id,
                               tenant_id=tenant_id,
                               auth_url=auth_url or settings.OPENSTACK_KEYSTONE_URL,
                               endpoint=endpoint)
    return c


def _keystoneclient_admin(service_token=settings.SERVICE_TOKEN, 
                          service_endpoint=settings.SERVICE_ENDPOINT):
    """
        To fake admin token.
    """
    return keystone_client.Client(token=service_token, endpoint=service_endpoint)


def simple_auth(username, password):
    """
    Do auth by username and password, return scoped token under certain tenant.
    """
    c = _keystoneclient(username, password)
    
    token = None
    
    tenants = c.tenants.list()
    while tenants:
        try:
            tenant = tenants.pop()
            token = c.tokens.authenticate(username=username, password=password, tenant_id=tenant.id)
            break
        except:
            pass
        
    return token


def token_create(username, password, tenant_id=None):
    '''
    Creates a token using the username and password provided. If tenant
    is provided it will retrieve a scoped token and the service catalog for
    the given tenant. Otherwise it will return an unscoped token and without
    a service catalog.
    '''
    c = _keystoneclient(username, password, tenant_id=tenant_id)
    
    return c.tokens.authenticate(username=username, password=password)

    
def tenant_list_for_token(token_id):
    c = _keystoneclient(token_id=token_id)
    
    return c.tenants.list()


def scoped_token_create(token_id, tenant_id):
    """
    Creates a scoped token using the tenant id and unscoped token; retrieves
    the service catalog for the given tenant.
    """
    c = _keystoneclient(tenant_id=tenant_id,
                       token_id=token_id)
    
    raw_token = c.tokens.authenticate(tenant_id=tenant_id,
                                      token=token_id,
                                      return_raw=True)
    
#    LOG.debug('got raw_token: %s' % raw_token)
    
    # FIXME need to modify c3 ?
#    c.service_catalog = service_catalog.ServiceCatalog(raw_token)
#    if request.ouser.is_admin():
#        c.management_url = c.service_catalog.url_for(service_type='identity',
#                                                     endpoint_type='adminURL')
#    else:
#        c.management_url = c.service_catalog.url_for(service_type='identity',
#                                                     endpoint_type='publicURL')
    scoped_token = tokens.Token(tokens.TokenManager, raw_token)
    return scoped_token


#TODO: cache it
DEFAULT_ROLE = None
def get_default_role(client):
    """
    Gets the default role object from Keystone and saves it as a global
    since this is configured in settings and should not change from request
    to request. Supports lookup by name or id.
    """
    global DEFAULT_ROLE
    default = getattr(settings, "OPENSTACK_KEYSTONE_DEFAULT_ROLE", None)
    if default and DEFAULT_ROLE is None:
        try:
            roles = client.roles.list()
        except Exception as e:
            LOG.error('Error when get roles list')
            LOG.error(e)
        else:
            for role in roles:
                if role.id == default or role.name.lower() == default:
                    DEFAULT_ROLE = role
                    break
    return DEFAULT_ROLE


def user_check_password(user_name, password):
    _keystoneclient(user_name, password)  # invalid password will raise an error


def user_update_password(user_id, password):
    return _keystoneclient_admin().users.update_password(user_id, password)


def user_create(username, email, password, tenant_id=None, enabled=True):
    c = _keystoneclient_admin()
    
    if tenant_id is None:
        tenant = c.tenants.create('%s_default_tenant' % username,
                                   'default tenant for %s' %username, 
                                    enabled=True) 
        tenant_id = tenant.id
        
    new_user = c.users.create(
                   username, password, email,
                   tenant_id=tenant_id,
                   enabled=enabled
                   )
    
    new_user.tenant_id = tenant_id  # for account balance initialization
    
    try:
        default_role = get_default_role(c)
        if default_role:
            c.roles.add_user_role(new_user.id, default_role.id, tenant_id)
    except Exception as e:
        LOG.error('Error when adding role %s for user %s at tenant %s' % (default_role, new_user, tenant_id)) 
        LOG.error(e)
        
    return new_user


def all_tenants_for_admin():
    c = _keystoneclient_admin()
    return c.tenants.list()

def list_all_user(tenant_id):
    c =_keystoneclient_admin()
    
    return c.users.list(tenant_id)

def get_user(user):
    c = _keystoneclient_admin()
    return c.users.get(user)