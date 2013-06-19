from novaclient.v1_1 import client as nova_client

import settings

import LOG
from api.utils import url_for


REBOOT_SOFT, REBOOT_HARD = 'SOFT', 'HARD'


def _novaclient(request, service_type='compute'):
    # service_type can not be 'volume'? 404 occurs
    user = request.ouser
    catalog = request.ouser.service_catalog
    #print catalog
    #LOG.debug('service_type is : %s' % service_type)
#    LOG.debug('service catalog is : %s' % catalog)
#    LOG.debug('novaclient connection created using token "%s" and url "%s"' %
#              (user.token, url_for(catalog, 'compute')))
    management_url = url_for(catalog, service_type)
    c = nova_client.Client(user.name,
                           user.token,
                           project_id=user.tenant_id,
                           auth_url=management_url)
    
    c.client.auth_token = user.token
    c.client.management_url = management_url
    
    return c


def _novaclient_admin(admin_username=settings.ADMIN_USER_NAME,
                      admin_password=settings.ADMIN_PASSWORD, 
                      admin_tenant=settings.ADMIN_TENANT):
    
    c = nova_client.Client(admin_username,admin_password, admin_tenant,
                           auth_url=settings.SERVICE_ENDPOINT, endpoint_type='adminURL')
    return c


def usage_list_for_admin(start, end):
    return _novaclient_admin().usage.list(start, end, True)


def server_suspend_for_admin(deficit_tenants):
    if not deficit_tenants:
        return
    
    c = _novaclient_admin()
    servers = c.servers.list(True, {'all_tenants': True})
    LOG.debug('Got %s servers: %s', len(servers), servers)
    for s in servers:
        try:
            LOG.debug('to suspend instance #%s under tenant #%s', s.id, s.tenant_id)
            if s.status.lower()=='active' and s.tenant_id in deficit_tenants:
                s.suspend()
        except Exception, e:
            LOG.error('error while suspending instance #%s under tenant #%s', s.id, s.tenant_id)
            LOG.exception(e)


def usage_get(request, tenant_id, start, end):
    return _novaclient(request).usage.get(tenant_id, start, end)


def server_list(request, search_opts=None, all_tenants=False):
    if search_opts is None:
        search_opts = {}
    if all_tenants:
        search_opts['all_tenants'] = True
    else:
        search_opts['project_id'] = request.ouser.tenant_id
    return _novaclient(request).servers.list(True, search_opts)  # fetch with detail

def server_get(request, instance_id):
    return _novaclient(request).servers.get(instance_id)

def server_create(request, name, image_id, flavor_id, key_name=None, user_data=None):
    return _novaclient(request).servers.create(
                    name, image_id, flavor_id, key_name=key_name, userdata=user_data)

def server_delete(request, instance_id):
    _novaclient(request).servers.delete(instance_id)

def server_suspend(request, instance_id):
    server_get(request, instance_id).suspend()

def server_resume(request, instance_id):
    server_get(request, instance_id).resume()

def server_reboot(request, instance_id, hardness=REBOOT_HARD):
    server_get(request, instance_id).reboot(hardness)

def flavor_list(request):
    return _novaclient(request).flavors.list()

def flavor_get(request, flavor_id):
    return _novaclient(request).flavors.get(flavor_id)

def security_group_list(request):
    return _novaclient(request).security_groups.list()

def security_group_get(request, security_group_id):
    return _novaclient(request).security_groups.get(security_group_id)

def security_group_create(request, name, description):
    return _novaclient(request).security_groups.create(name, description)

def security_group_delete(request, security_group_id):
    _novaclient(request).security_groups.delete(security_group_id)

def security_group_rule_create(request, parent_group_id, ip_protocol=None,
                               from_port=None, to_port=None, cidr=None, group_id=None):
    
    return _novaclient(request).security_group_rules.create(
                                                        parent_group_id,
                                                        ip_protocol,
                                                        from_port,
                                                        to_port,
                                                        cidr,
                                                        group_id)

def security_group_rule_delete(request, security_group_rule_id):
    _novaclient(request).security_group_rules.delete(security_group_rule_id)

def keypair_list(request):
    return _novaclient(request).keypairs.list()

def keypair_create(request, name):
    return _novaclient(request).keypairs.create(name)

def keypair_import(request, name, public_key):
    return _novaclient(request).keypairs.create(name, public_key)

def keypair_delete(request, keypair_name):
    _novaclient(request).keypairs.delete(keypair_name)

def image_list(request, detailed=True):
    return _novaclient(request).images.list(detailed)

def snapshot_list(request, detailed=True):
    # you need to do filter by your own :(
    return image_list(request, detailed)

def image_get(request, image_id):
    return _novaclient(request).images.get(image_id)

def image_update(request, image_id, metadata):
    return _novaclient(request).images.set_meta(image_id, metadata)

def image_delete(request, image_id):
    _novaclient(request).images.delete(image_id)

def snapshot_create(request, instance_id, name):
    return _novaclient(request).servers.create_image(instance_id, name)

def server_vnc_console(request, instance_id, console_type='novnc'):
    return _novaclient(request).servers.get_vnc_console(instance_id, console_type)['console']

def server_console_output(request, instance_id, tail_length=None):
    return _novaclient(request).servers.get_console_output(instance_id, length=tail_length)

def server_add_floating_ip(request, instance_id, floating_ip_id):
    """Associates floating IP to server's fixed IP.
    """
    fip = tenant_floating_ip_get(request, floating_ip_id)
    return _novaclient(request).servers.add_floating_ip(instance_id, fip)

def server_remove_floating_ip(request, instance_id, floating_ip_id):
    """Removes relationship between floating and server's fixed ip.
    """
    fip = tenant_floating_ip_get(request, floating_ip_id)
    return _novaclient(request).servers.remove_floating_ip(instance_id, fip)

def volume_list(request):
    return _novaclient(request).volumes.list()

def volume_create(request, size, name, description):
    return _novaclient(request).volumes.create(size, 
            display_name=name,
            display_description=description)

def volume_delete(request, volume_id):
    _novaclient(request).volumes.delete(volume_id)

def volume_get(request, volume_id):
    return _novaclient(request).volumes.get(volume_id)

def volume_attach(request, volume_id, instance_id, device):
    _novaclient(request).volumes.create_server_volume(instance_id,
                                                     volume_id,
                                                     device)

def volume_detach(request, instance_id, attachment_id):
    _novaclient(request).volumes.delete_server_volume(
            instance_id, attachment_id)
    
def tenant_floating_ip_list(request):
    """Fetches a list of all floating ips."""
    return _novaclient(request).floating_ips.list()

def tenant_floating_ip_get(request, floating_ip_id):
    """Fetches a floating ip."""
    return _novaclient(request).floating_ips.get(floating_ip_id)

def tenant_floating_ip_allocate(request, pool=None):
    """Allocates a floating ip to tenant. Optionally you may provide a pool
    for which you would like the IP.
    """
    return _novaclient(request).floating_ips.create(pool=pool)    

def floating_ip_pools_list(request):
    """Fetches a list of all floating ip pools."""
    return _novaclient(request).floating_ip_pools.list()