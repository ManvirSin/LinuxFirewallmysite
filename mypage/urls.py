from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from mypage.views import (
    FirewallRuleFormView, home, login_view, firewall_view, accountdets_view,
    configuration_view, dashboard_view, logout_view, modify_firewall_rule,
    delete_firewall_rule, get_firewall_rules, natconfig_view,
    get_nat_rules, delete_nat_rule, update_account
)
from mypage.views import AccountView

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('accountdets/', accountdets_view, name='accountdets'),
    path('accountdets/update/', update_account, name='update_account'),
    path('configuration/', FirewallRuleFormView.as_view(), name='configuration'),
    path('natconfig/', natconfig_view, name='natconfig'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('create_account/', AccountView.as_view(), name='create_account'),
    path('update_account/', update_account, name='update_account'),
    path('firewall/', firewall_view, name='firewall'),
    path('dashboard/modify_nat_rule/<int:rule_id>/', views.modify_nat_rule, name='modify_nat_rule'),
    path('get_nat_rules/', get_nat_rules, name='get_nat_rules'),
    path('delete_nat_rule/<int:rule_id>/', delete_nat_rule, name='delete_nat_rule'),
    path('modify_firewall_rule/<int:rule_id>/', modify_firewall_rule, name='modify_firewall_rule'),
    path('get_firewall_rules/', get_firewall_rules, name='get_firewall_rules'),
    path('delete_firewall_rule/<int:rule_id>/', delete_firewall_rule, name='delete_firewall_rule'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

