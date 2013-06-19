import sys
from api.openstack import keystone as keystone_api
from api.openstack import nova as nova_api
from api.sortdict import SortedDict
from api.openstack import settings
from api.scanner.utils import get_port_config


def _extra_instance(request, instance, detailed=False, full_flavors=None):
    #instance.ips = utils.get_ips(instance)  #TODO: show IP by template tag
    
    # to get size
    if full_flavors is None:
        flavors = nova_api.flavor_list(request)
        full_flavors = SortedDict([(str(flavor.id), flavor) for flavor in flavors])
    instance.full_flavor = full_flavors[instance.flavor['id']]
    #instance.size = utils.get_size(instance)
    instance.is_ajax_stating = False  # flag to tell state updating by AJAX, default as True
    
    if detailed:
        instance.power_state = settings.POWER_STATES.get(getattr(instance, "OS-EXT-STS:power_state", 0), '')
        instance.task = getattr(instance, 'OS-EXT-STS:task_state', '')
        instance.physical_host = getattr(instance,'OS-EXT-SRV-ATTR:host','')
        #instance.ips = utils.get_ips(instance)  #TODO: show IP by template tag
        instance.is_transitionary = instance.status and instance.status.upper() not in settings.FINAL_STATUS
        instance.loading_status = instance.task or instance.is_transitionary
        if instance.created: # it is not datetime type :(
            time_str = instance.created
            instance.created = time_str.replace('T', ' ').replace('Z', '')
        
    return instance


class User(object):
    """
        This is Openstack's user, which is managed by Keystone.
    """
    def __init__(self, id=None, account_id=None, token=None, name=None, tenant_id=None,
                    service_catalog=None, tenant_name=None, roles=None, authorized_tenants=None):
        self.id = id
        self.account_id = account_id
        self.token = token
        self.name = name
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.service_catalog = service_catalog
        self.roles = roles or []
        self.authorized_tenants = authorized_tenants
        
    @property
    def has_login_openstack(self):
        return self.tenant_id

    def is_authenticated(self):
        # TODO: deal with token expiration
        return self.token

    def is_admin(self):
        for role in self.roles:
            if role['name'].lower() == 'admin':
                return True
        return False

class Request(object):
    def __init__(self):
        pass
    
    def __setattr__(self,name,value):
        object.__setattr__(self,name,value)

def _set_request_data(request,token):
    request.session = dict()
    request.session['serviceCatalog'] = token.serviceCatalog
    request.session['tenant'] = token.tenant['name']
    request.session['tenant_id'] = token.tenant['id']
    request.session['token'] = token.id
    request.session['user_id'] = token.user['id']
    request.session['roles'] = token.user['roles']
    request.session['user_name'] = 'admin'


def checker_uuid(uuid):
    request = Request()
    
    token = keystone_api.token_create(settings.ADMIN_USER_NAME, settings.ADMIN_PASSWORD)
    
    tenants = keystone_api.tenant_list_for_token(token.id)
    
    while tenants:
        tenant = tenants.pop()
        try:
            token = keystone_api.scoped_token_create(token.id, tenant.id)
            break
        except Exception, e:
            token = None
    
    _set_request_data(request,token)
    
    
    request.ouser = User()
    
    request.ouser = User(id=request.session['user_id'],
                        #account_id=request.session['account_id'],
                        token=request.session['token'],
                        name=request.session['user_name'],
                        tenant_id=request.session['tenant_id'],
                        tenant_name=request.session['tenant'],
                        service_catalog=request.session['serviceCatalog'],
                        roles=request.session['roles'])
    try:
        ins = nova_api.server_get(request,uuid)
    except:
        return False
    else:
        return True


def checker():
    request = Request()
    
    token = keystone_api.simple_auth(settings.ADMIN_USER_NAME,settings.ADMIN_PASSWORD)
    
    _set_request_data(request,token)
    
    
    request.ouser = User()
    
    request.ouser = User(id=request.session['user_id'],
                        token=request.session['token'],
                        name=request.session['user_name'],
                        tenant_id=request.session['tenant_id'],
                        tenant_name=request.session['tenant'],
                        service_catalog=request.session['serviceCatalog'],
                        roles=request.session['roles'])
    
    instances = nova_api.server_list(request,all_tenants=True)
    
    flavors = nova_api.flavor_list(request)
    full_flavors = SortedDict([(str(flavor.id), flavor) for flavor in flavors])
    for instance in instances:
        _extra_instance(request, instance, detailed=True, full_flavors=full_flavors)
    
    ins_list = list()
    for i in instances:
        ins = dict()
        ins['ip_address'] = i.addresses
        ins['name'] = i.name
        ins['power_state'] = i.power_state
        ins['id'] = i.id
        ins['physical_host'] = i.physical_host
        ins['full_flavor'] = i.full_flavor.id
        ins_list.append(ins)
    #return ins_list

    instance_id = '1e79faf8-7522-42b0-8034-9a108cf11ee2'
    
    snapshots = nova_api.snapshot_list(request, detailed=True)
    for snapshot in snapshots:
        src_server_id = getattr(snapshot,'server',{}).get('id',None)
        if src_server_id == instance_id:
            image_id = snapshot.id
            break
    
    if src_server_id:
        server_instance = nova_api.server_get(request,src_server_id)
        
        flavor_id = server_instance.flavor.get('id')
        name = server_instance.name + '-lb'
        
        second_instance = nova_api.server_create(request,name,image_id,flavor_id,key_name=None,user_data=None)
        
        lb_first_instance = server_instance
        lb_second_instance = second_instance
        
    else:
        print "%s has no snapshot!" % instance_id

if __name__ == '__main__':
    checker()

