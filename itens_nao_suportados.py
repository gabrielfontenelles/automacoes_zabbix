from zabbix_api import ZabbixAPI
import urllib3
urllib3.disable_warnings()


ZABBIX_SERVER = 'https://seu-zabbix.com'
ZABBIX_TOKEN = 'token da api'
HOST_GROUP = 'DESATIVADOS'

def connect_zabbix():
    zapi = ZabbixAPI(ZABBIX_SERVER)
    zapi.login(api_token=ZABBIX_TOKEN)
    return zapi

def get_disabled_group_hosts(zapi):
   
    group = zapi.hostgroup.get({
        'output': ['groupid'],
        'filter': {
            'name': HOST_GROUP
        }
    })
    
    if not group:
        raise Exception(f"Grupo '{HOST_GROUP}' não encontrado!")
    
    
    hosts = zapi.host.get({
        'output': ['hostid', 'host'],
        'groupids': group[0]['groupid']
    })
    
    return hosts

def disable_unsupported_items():
    try:
        zapi = connect_zabbix()
        print("Conectado ao Zabbix com sucesso!")
        
        
        hosts = get_disabled_group_hosts(zapi)

        if not hosts:
            print(f"Nenhum host encontrado no grupo {HOST_GROUP}!")
            return

        print(f"\nHosts encontrados no grupo {HOST_GROUP} ({len(hosts)}):")
        for host in hosts:
            print(f"- {host['host']}")

        total_items_disabled = 0
        hosts_processados = 0
        
        for host in hosts:
            print(f"\nProcessando host: {host['host']}")
            hosts_processados += 1

            
            unsupported_items = zapi.item.get({
                'hostids': host['hostid'],
                'filter': {
                    'state': 1  # 1 = não suportado
                },
                'output': ['itemid', 'name', 'status']
            })

            if not unsupported_items:
                print("Nenhum item não suportado encontrado neste host.")
                continue

            
            host_items_disabled = 0
            for item in unsupported_items:
                if item['status'] == '0':  # 0 = ativo
                    try:
                        zapi.item.update({
                            'itemid': item['itemid'],
                            'status': 1  # 1 = desativado
                        })
                        print(f"Item desativado: {item['name']}")
                        host_items_disabled += 1
                        total_items_disabled += 1
                    except Exception as e:
                        print(f"Erro ao desativar item {item['name']}: {e}")

            print(f"Total de itens desativados neste host: {host_items_disabled}")

        print(f"\nResumo final:")
        print(f"Total de hosts encontrados: {len(hosts)}")
        print(f"Hosts processados: {hosts_processados}")
        print(f"Total de itens desativados: {total_items_disabled}")

    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == '__main__':
    disable_unsupported_items()