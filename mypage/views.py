import os
from turtle import update
from django.views import View
import paramiko
from subprocess import run, PIPE
from paramiko import SSHClient, AutoAddPolicy
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, FirewallRuleForm, NatRuleForm, UserCreateForm
from .models import FirewallRule, NAT, CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.utils.decorators import method_decorator
from .ssh import connect_ssh, generate_iptables_command

class BaseFirewallView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
@method_decorator(login_required, name='dispatch')
class ConfigurationView(CreateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['firewall_ip'] = settings.FIREWALL_IP
        return context
    
@method_decorator(login_required, name='dispatch')
class UpdateFirewallRuleView(UpdateView):
    model = FirewallRule
    form_class = FirewallRuleForm
    template_name = 'update_firewall_rule.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)

        iptables_command = generate_iptables_command(self.object, update=True)
        ssh_client = connect_ssh()
        ssh_client.exec_command(iptables_command)
        ssh_client.close()

        messages.success(self.request, 'Firewall rule updated successfully!')
        return response
    
@method_decorator(login_required, name='dispatch')
class DashboardView(ListView):
    template_name = 'dashboard.html'
    context_object_name = 'firewall_rules'

    def get_queryset(self):
        return FirewallRule.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nat_rules'] = NAT.objects.filter(user=self.request.user)
        return context

class FirewallRuleFormView(BaseFirewallView, CreateView):
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['firewall_ip'] = '192.168.48.135'  # example firewall IP
        return context

class ModifyFirewallRuleView(BaseFirewallView, UpdateView):
    model = FirewallRule
    form_class = FirewallRuleForm
    template_name = 'configuration.html'
    pk_url_kwarg = 'rule_id'
    success_url = reverse_lazy('configuration')

class DeleteFirewallRuleView(BaseFirewallView, DeleteView):
    model = FirewallRule
    pk_url_kwarg = 'rule_id'

    def delete(self, request, *args, **kwargs):
        try:
            rule = self.get_object()
            rule.delete()
            return JsonResponse({'status': 'success'})
        except FirewallRule.DoesNotExist:
            return JsonResponse({'status': 'failure'})

class GetFirewallRulesView(BaseFirewallView, ListView):
    model = FirewallRule

    def get(self, request, *args, **kwargs):
        rules = self.get_queryset()
        rules_data = [{'name': rule.name, 'rule': rule.rule} for rule in rules]
        return JsonResponse(rules_data, safe=False)

class NatConfigView(FormView):
    form_class = NatRuleForm
    template_name = 'natconfig.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['firewall_ip'] = settings.FIREWALL_IP
        return initial

    def form_valid(self, form):
        # The code from your natconfig_view function goes here
        user = CustomUser.objects.get(username=self.request.user.username)
        source_ip = settings.FIREWALL_IP
        destination_ip = form.cleaned_data['destination_ip']
        protocol = form.cleaned_data['protocol']
        source_port = form.cleaned_data['source_port']
        destination_port = form.cleaned_data['destination_port']

        # Save the form to a new_nat_rule object without committing it to the database yet
        new_nat_rule = form.save(commit=False)

        # Set the user for the new NAT rule
        new_nat_rule.user = self.request.user

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

        # Read the NAT table from the Linux machine
        stdin, stdout, stderr = ssh.exec_command('sudo iptables -t nat -L')

        # Save the new_nat_rule to the database
        new_nat_rule.save()

        ssh.close()

        messages.success(self.request, 'NAT rule added successfully!')
        return redirect('dashboard')  # Redirect to dashboard page after successfully submitting form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['source_ip'] = settings.FIREWALL_IP
        return context

natconfig_view = login_required(NatConfigView.as_view())

@method_decorator(login_required, name='dispatch')
class DeleteNatRuleView(DeleteView):
    model = NAT
    success_url = reverse_lazy('dashboard')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

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
def profile_view(request):
    # Your profile view logic here
    return render(request, 'profile.html')

    

class FirewallView(TemplateView):
    template_name = 'configuration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ssh = connect_ssh()
        stdin, stdout, stderr = ssh.exec_command('iptables -L')
        output = stdout.read()
        ssh.close()
        context['output'] = output.decode('utf-8')
        return context

firewall_view = login_required(FirewallView.as_view())

def configure_firewall(request):
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, firewall_ip=settings.FIREWALL_IP)
        if form.is_valid():
            # Retrieve the form data
            rule_name = form.cleaned_data['rule_name']
            chain = form.cleaned_data['chain']
            source_ip = settings.FIREWALL_IP
            destination_ip = form.cleaned_data['destination_ip']
            protocol = form.cleaned_data['protocol']
            source_port = form.cleaned_data['source_port']
            destination_port = form.cleaned_data['destination_port']
            action = form.cleaned_data['action']
            log_traffic = form.cleaned_data['log_traffic']
            alert_user = form.cleaned_data['alert_user']
            
            # Create a new firewall rule object
            new_rule = FirewallRule(user=request.user, rule_name=rule_name, chain=chain,
                                    source_ip=source_ip, destination_ip=destination_ip,
                                    protocol=protocol, source_port=source_port,
                                    destination_port=destination_port, action=action,
                                    log_traffic=log_traffic, alert_user=alert_user)
            
            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(settings.FIREWALL_IP, username=settings.FIREWALL_USERNAME, password=settings.FIREWALL_PASSWORD)
            
            # Generate the iptables command using the new function
            iptables_command = generate_iptables_command(new_rule)

            # Print the iptables command for debugging purposes
            print("Generated iptables command:", iptables_command)

            # Execute the iptables command
            stdin, stdout, stderr = ssh.exec_command(iptables_command)

            # Print the output and errors for debugging purposes
            print("Output:", stdout.read())
            print("Errors:", stderr.read())

            ssh.close()
            
            # Save the new rule to the database
            new_rule.save()

            # Redirect to the configuration page with a success message
            messages.success(request, 'Firewall rule added successfully!')
            return redirect('dashboard')
        else:
            # Render the configuration page with the form and errors
            return render(request, 'configuration.html', {'form': form})
    else:
        # Render the configuration page with the form
        form = FirewallRuleForm()
        return render(request, 'configuration.html', {'form': form})
    
def dashboard(request):
    if request.method == 'POST':
        firewall_form = FirewallRuleForm(request.POST, prefix='firewall_form')
        nat_form = NatRuleForm(request.POST, prefix='nat_form')

        if firewall_form.is_valid():
            firewall_rule = firewall_form.save(commit=False)
            firewall_rule.user = request.user
            firewall_rule.save()

        if nat_form.is_valid():
            nat_rule = nat_form.save(commit=False)
            nat_rule.user = request.user
            nat_rule.save()

    else:
        firewall_form = FirewallRuleForm(prefix='firewall_form')
        nat_form = NatRuleForm(prefix='nat_form')

    firewall_rules = FirewallRule.objects.filter(user=request.user)
    nat_rules = NatRuleForm.objects.filter(user=request.user)

    context = {
        'firewall_rules': firewall_rules,
        'nat_rules': nat_rules,
        'firewall_form': firewall_form,
        'nat_form': nat_form,
    }


def natconfig(request):
    if request.method == 'POST':
        form = NatRuleForm(request.POST)
        if form.is_valid():
            nat_rule = form.save(commit=False)
            nat_rule.user = request.user
            nat_rule.save()
            return redirect('dashboard')
    else:
        form = NatRuleForm()

    context = {'form': form}
    return render(request, 'natconfig.html', context)


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
    user = request.user
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
    return render(request, 'configuration.html', {'form': form, 'user': request.user, 'source_ip': settings.FIREWALL_IP})

class UpdateFirewallRuleView(UpdateView):
    model = FirewallRule
    form_class = FirewallRuleForm
    template_name = 'update_firewall_rule.html'

    def form_valid(self, form):
        updated_rule = form.save(commit=False)
        updated_rule.user = self.request.user
        updated_rule.save()

        # Modify this function to handle updates as well
        iptables_command = generate_iptables_command(updated_rule, update=True)
        ssh_client = connect_ssh()
        ssh_client.exec_command(iptables_command)
        ssh_client.close()

        messages.success(self.request, 'Firewall rule updated successfully!')
        return redirect('dashboard')

update_firewall_rule = login_required(UpdateFirewallRuleView.as_view())

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['firewall_rules'] = FirewallRule.objects.filter(user=user)
        context['nat_rules'] = NAT.objects.filter(user=user)
        context['user'] = user
        return context

dashboard_view = login_required(DashboardView.as_view())

class ModifyFirewallRuleView(UpdateView):
    model = FirewallRule
    form_class = FirewallRuleForm
    template_name = 'configuration.html'

    def get_success_url(self):
        return reverse('configuration')

modify_firewall_rule = login_required(ModifyFirewallRuleView.as_view())

class DeleteFirewallRuleView(DeleteView):
    model = FirewallRule

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'})

delete_firewall_rule = login_required(DeleteFirewallRuleView.as_view())

class GetFirewallRulesView(View):
    def get(self, request):
        rules = FirewallRule.objects.all()
        rules_data = [{'name': rule.name, 'rule': rule.rule} for rule in rules]
        return JsonResponse(rules_data, safe=False)

get_firewall_rules = login_required(GetFirewallRulesView.as_view())

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
            
            # Read the NAT table from the Linux machine
            stdin, stdout, stderr = ssh.exec_command('sudo iptables -t nat -L')
            
            # Save the new_nat_rule to the database
            new_nat_rule.save()

            ssh.close()

            messages.success(request, 'NAT rule added successfully!')
            return redirect('dashboard')  # Redirect to dashboard page after successfully submitting form
        else:
            # Render the NAT configuration page with the form and errors
            return render(request, 'natconfig.html', {'form': form, 'user': user, 'firewall_ip': settings.FIREWALL_IP})
    else:
        form = NatRuleForm(firewall_ip=settings.FIREWALL_IP)
    return render(request, 'natconfig.html', {'form': form, 'user': user, 'source_ip': settings.FIREWALL_IP})
class ClearNatRulesView(View):
    def get(self, request):
        NAT.objects.all().delete()
        return redirect('dashboard')

clear_nat_rules = login_required(ClearNatRulesView.as_view())

class GetNatRulesView(View):
    def get(self, request):
        nat_rules = NAT.objects.all().values()
        return JsonResponse(list(nat_rules), safe=False)

get_nat_rules = login_required(GetNatRulesView.as_view())

class DeleteNatRuleView(DeleteView):
    model = NAT
    success_url = reverse_lazy('dashboard')

delete_nat_rule = login_required(DeleteNatRuleView.as_view())
class ModifyNatRuleView(UpdateView):
    model = NAT
    form_class = NatRuleForm
    template_name = 'modify_nat_rule.html'
    success_url = reverse_lazy('dashboard')

modify_nat_rule = login_required(ModifyNatRuleView.as_view())
