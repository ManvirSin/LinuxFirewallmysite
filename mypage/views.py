import os
import paramiko
from subprocess import run, PIPE
from paramiko import SSHClient, AutoAddPolicy
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, FirewallRuleForm, NatRuleForm, UserCreateForm
from .models import FirewallRule, NAT, CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required

FIREWALL_IP = os.getenv('FIREWALL_IP')
FIREWALL_USERNAME = os.getenv('FIREWALL_USERNAME')
FIREWALL_PASSWORD = os.getenv('FIREWALL_PASSWORD')

def connect_ssh():
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(settings.FIREWALL_IP, username=settings.FIREWALL_USERNAME, password=settings.FIREWALL_PASSWORD)
    return ssh_client


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')



@login_required
def firewall_view(request):
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('iptables -L')
    output = stdout.read()
    ssh.close()
    return render(request, 'configuration.html', {'output': output.decode('utf-8')})

def configure_firewall(request):
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, firewall_ip=settings.FIREWALL_IP)
        if form.is_valid():
            rule_name = form.cleaned_data['rule_name']
            direction = form.cleaned_data['direction']
            ip_address = form.cleaned_data['ip_address']
            traffic_type = form.cleaned_data['traffic_type']
            port_number = form.cleaned_data['port_number']
            protocol_type = form.cleaned_data['protocol_type']
            log_traffic = form.cleaned_data['log_traffic']
            alert_user = form.cleaned_data['alert_user']
            
            #saves the form to a new rule object without committing to the database yet
            new_rule = form.save(commit=False)
            
            new_rule.user = request.user

            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(FIREWALL_IP, username=FIREWALL_USERNAME, password=FIREWALL_PASSWORD)
            
           # Generate the iptables command using the new function
            iptables_command = generate_iptables_command(new_rule)

            # Execute the iptables command
            stdin, stdout, stderr = ssh.exec_command(iptables_command)
            ssh.close()
            
            #saves the new rule to the database
            new_rule.save()

            # Redirect to the configuration page with a success message
            messages.success(request, 'Firewall rule added successfully!')
            return redirect('natconfig.html')
        else:
            # Render the configuration page with the form and errors
            return render(request, 'configuration.html', {'form': form})
    else:
        # Render the configuration page with the form
        form = FirewallRuleForm()
        return render(request, 'configuration.html', {'form': form})

def create_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            login(request, user)
            print("User created successfully:", username)  # Add this line
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_account.html', {'form': form})


class AccountView(CreateView):
    form_class = UserCreateForm
    template_name = 'create_account.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

User = get_user_model()


@login_required
def update_account(request):
    if request.method == 'POST':
        # Retrieve the current user instance based on the user ID
        user = request.user

        # Update the fields with the new values submitted in the form
        user.name = request.POST.get('name')
        user.surname = request.POST.get('surname')
        user.email = request.POST.get('email')

        # Update username if it's not empty
        new_username = request.POST.get('username')
        if new_username:
            user.username = new_username

        # If a new password was submitted, update it too
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)

        user.save()

        # Add a success message
        messages.success(request, 'Account details updated successfully.')

        # Redirect the user back to the account details page
        return redirect('accountdets')

    else:
        # Render the account details page with the current user instance
        user = request.user
        return render(request, 'accountdets.html', {'user': user})


@login_required
def accountdets_view(request):
    user = CustomUser.objects.get(username=request.user.username)
    return render(request, 'accountdets.html', {'user': user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def configuration_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        form = FirewallRuleForm(request.POST)  # pass request.user as user argument
        if action == 'add':
            if form.is_valid():
                new_rule = form.save(commit=False)
                new_rule.user = request.user
                new_rule.save()
                return redirect('dashboard')  # Redirect to dashboard page after successfully submitting form
        elif action == 'clear':
            # Add the code to clear rules
            return redirect('configuration')  # Redirect to configuration page after clearing the rules
    else:
        form = FirewallRuleForm(user=request.user)  # Pass request.user as user argument()

    context = {
        'form': form,
        'user': request.user,
        'firewall_ip': settings.FIREWALL_IP,
    }
    return render(request, 'configuration.html', context)

def generate_iptables_command(rule):
    iptables_cmd = f"iptables -A {rule.direction.upper()} -p {rule.protocol_type}"

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

    return iptables_cmd


@login_required
def dashboard_view(request):
    user = request.user  # Use the request.user object directly
    firewall_rules = FirewallRule.objects.filter(user=user)  # Filter rules by the logged-in user
    nat_rules = NAT.objects.filter(user=user)  # Filter NAT rules by the logged-in user
    context = {
        'firewall_rules': firewall_rules,
        'user': user,
        'nat_rules': nat_rules,
    }

    print("Firewall Rules:", firewall_rules, "NAT Rules:", nat_rules)  # Add this line to print the firewall and NAT rules

    return render(request, 'dashboard.html', context)


class FirewallRuleFormView(CreateView):
    form_class = FirewallRuleForm
    template_name = 'configuration.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the user field
        response = super().form_valid(form)
        
        # Generate iptables command and execute it on the remote Linux machine
        iptables_cmd = generate_iptables_command(form.instance)
        ssh_client = connect_ssh()
        ssh_client.exec_command(iptables_cmd)
        ssh_client.close()

        return response


def modify_firewall_rule(request, rule_id):
    rule = FirewallRule.objects.get(pk=rule_id)
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            return redirect('configuration')
    else:
        form = FirewallRuleForm(instance=rule)
    return render(request, 'configuration.html', {'form': form, 'rule': rule})


def delete_firewall_rule(request, rule_id):
    try:
        rule = FirewallRule.objects.get(pk=rule_id)
        rule.delete()
        return JsonResponse({'status': 'success'})
    except FirewallRule.DoesNotExist:
        return JsonResponse({'status': 'failure'})

def get_firewall_rules(request):
    rules = FirewallRule.objects.all()
    rules_data = [{'name': rule.name, 'rule': rule.rule} for rule in rules]
    return JsonResponse(rules_data, safe=False)

@login_required
def natconfig_view(request):
    user = CustomUser.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = NatRuleForm(request.POST, firewall_ip=settings.FIREWALL_IP)
        if form.is_valid():
            source_ip = settings.FIREWALL_IP
            destination_ip = form.cleaned_data['destination_ip']
            protocol = form.cleaned_data['protocol']
            source_port = form.cleaned_data['source_port']
            destination_port = form.cleaned_data['destination_port']

            # Save the form to a new_nat_rule object without committing it to the database yet
            new_nat_rule = form.save(commit=False)

            # Set the user for the new NAT rule
            new_nat_rule.user = request.user

            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(settings.FIREWALL_IP, username=settings.FIREWALL_USERNAME, password=settings.FIREWALL_PASSWORD)

            # Construct the iptables command for DNAT
            iptables_dnat_command = f"sudo iptables -t nat -A PREROUTING -p {protocol} --dport {source_port} -j DNAT --to-destination {destination_ip}:{destination_port}"

            # Execute the iptables command for DNAT
            stdin, stdout, stderr = ssh.exec_command(iptables_dnat_command)

            # Construct the iptables command for SNAT
            iptables_snat_command = f"sudo iptables -t nat -A POSTROUTING -p {protocol} --dport {destination_port} -d {destination_ip} -j SNAT --to-source {source_ip}"

            # Execute the iptables command for SNAT
            stdin, stdout, stderr = ssh.exec_command(iptables_snat_command)

            ssh.close()

            # Save the new_nat_rule to the database
            new_nat_rule.save()

            messages.success(request, 'NAT rule added successfully!')
            return redirect('dashboard')  # Redirect to dashboard page after successfully submitting form
        else:
            # Render the NAT configuration page with the form and errors
            return render(request, 'natconfig.html', {'form': form, 'user': user, 'firewall_ip': settings.FIREWALL_IP})
    else:
        form = NatRuleForm(firewall_ip=settings.FIREWALL_IP)
    return render(request, 'natconfig.html', {'form': form, 'user': user, 'firewall_ip': settings.FIREWALL_IP})



@login_required
def clear_nat_rules(request):
    NAT.objects.all().delete()
    return redirect('dashboard')

@login_required
def get_nat_rules(request):
    nat_rules = NAT.objects.all().values()
    return JsonResponse(list(nat_rules), safe=False)

@login_required
def delete_nat_rule(request, rule_id):
    rule = get_object_or_404(NAT, pk=rule_id)
    rule.delete()
    return redirect('dashboard')

@login_required
def modify_nat_rule(request, rule_id):
    rule = get_object_or_404(NAT, id=rule_id)
    form = NatRuleForm(request.POST or None, instance=rule)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    else:
        form = NatRuleForm(instance=rule)
    return render(request, 'modify_nat_rule.html', {'form': form, 'rule': rule})
