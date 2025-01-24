from zabbix_api import ZabbixAPI
import urllib3
urllib3.disable_warnings()

# Configurações de conexão
ZABBIX_SERVER = 'LINK DO ZABBIX'
ZABBIX_TOKEN = 'TOKEN DA API'

def connect_zabbix():
    zapi = ZabbixAPI(ZABBIX_SERVER)
    zapi.login(api_token=ZABBIX_TOKEN)
    return zapi

def remove_disabled_host_templates(zapi):
    # Buscar hosts desativados
    disabled_hosts = zapi.host.get({
        'filter': {'status': 1},
        'output': ['hostid', 'host'],
        'selectParentTemplates': ['templateid']
    })

    for host in disabled_hosts:
        # Remover templates dos hosts desativados (apenas unlink)
        if host['parentTemplates']:
            template_ids = [template['templateid'] for template in host['parentTemplates']]
            zapi.host.update({
                'hostid': host['hostid'],
                'templates_clear': template_ids
            })

def update_proxy_and_hostgroups(zapi):
    # Buscar hosts desativados
    disabled_hosts = zapi.host.get({
        'filter': {'status': 1},
        'output': ['hostid', 'host'],
        'selectHostGroups': ['groupid', 'name']
    })

    # Encontrar ou criar grupo 'DESATIVADOS'
    desativados_group = zapi.hostgroup.get({
        'filter': {'name': 'DESATIVADOS'}
    })

    if not desativados_group:
        desativados_group = zapi.hostgroup.create({'name': 'DESATIVADOS'})
        desativados_group = [{'groupid': desativados_group['groupids'][0]}]

    for host in disabled_hosts:
        # Remover todos os grupos atuais e adicionar grupo 'DESATIVADOS'
        zapi.host.update({
            'hostid': host['hostid'],
            'groups': desativados_group,
            'proxy_hostid': 0  # Define para (no proxy)
        })

def main():
    try:
        zapi = connect_zabbix()
        remove_disabled_host_templates(zapi)
        update_proxy_and_hostgroups(zapi)
        print("Limpeza de hosts desativados concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == '__main__':
    main()