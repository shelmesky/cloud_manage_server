from api.exceptions import NotAuthorized, ServiceCatalogException

def _get_service_from_catalog(catalog, service_type):
    if catalog:
        for service in catalog:
            if service['type'] == service_type:
                return service
    return None

def url_for(catalog, service_type, admin=False, endpoint_type='internalURL'):
    if not catalog:
        raise NotAuthorized('service catalog is empty, need to relogin')
        
    service = _get_service_from_catalog(catalog, service_type)
    
    try:
        if admin:
            return service['endpoints'][0]['adminURL']
        else:
            return service['endpoints'][0][endpoint_type]
    except (IndexError, KeyError):
        raise ServiceCatalogException('no service - %s' % service_type)
    