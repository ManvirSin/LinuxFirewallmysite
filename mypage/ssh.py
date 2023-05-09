import os
from turtle import update
from paramiko import AutoAddPolicy, SSHClient
from Firewallsite import settings


FIREWALL_IP = os.getenv('FIREWALL_IP')
FIREWALL_USERNAME = os.getenv('FIREWALL_USERNAME')
FIREWALL_PASSWORD = os.getenv('FIREWALL_PASSWORD')

def connect_ssh():
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(settings.FIREWALL_IP, username=settings.FIREWALL_USERNAME, password=settings.FIREWALL_PASSWORD)
    return ssh_client

def generate_iptables_command(rule):
    iptables_cmd = f"iptables -{'R' if update else 'A'} {rule.direction.upper()} -p {rule.protocol_type}"
    
    if update:
        iptables_cmd += f" {rule.rule_number}"

    if rule.ip_address:
        iptables_cmd += f" -s {rule.ip_address}"

    if rule.port_number:
        iptables_cmd += f" --dport {rule.port_number}"

    if rule.traffic_type:
        iptables_cmd += f" -m {rule.traffic_type}"

    if rule.log_traffic:
        iptables_cmd += " -j LOG"

    if rule.alert_user:
        iptables_cmd += " -j ALERT"
        
    iptables_cmd += f" -j {rule.action}"

    return iptables_cmd