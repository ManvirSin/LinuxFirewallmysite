from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic.edit import FormView
from mypage.views import DeleteNatRuleView
from mypage import views
from mypage.views import AccountView, FirewallRuleFormView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accountdets/', views.accountdets_view, name='accountdets'),
    path('accountdets/update/', views.update_account, name='update_account'),
    path('configuration/', FirewallRuleFormView.as_view(), name='configuration'),
    path('configuration/<int:pk>/', views.ConfigurationView.as_view(), name='configuration'),
    path('natconfig/', views.natconfig_view, name='natconfig'),
    path('create_account/', AccountView.as_view(), name='create_account'),
    path('update_account/', views.update_account, name='update_account'),
    path('firewall/update/<int:pk>/', views.update_firewall_rule, name='update_firewall_rule'),
    path('firewall/', views.firewall_view, name='firewall'),
    path('dashboard/modify_nat_rule/<int:rule_id>/', views.modify_nat_rule, name='modify_nat_rule'),
    path('get_nat_rules/', views.get_nat_rules, name='get_nat_rules'),
    path('delete_nat_rule/<int:pk>/', DeleteNatRuleView.as_view(), name='delete_nat_rule'),
    path('modify_firewall_rule/<int:rule_id>/', views.modify_firewall_rule, name='modify_firewall_rule'),
    path('get_firewall_rules/', views.get_firewall_rules, name='get_firewall_rules'),
    path('delete_firewall_rule/<int:rule_id>/', views.delete_firewall_rule, name='delete_firewall_rule'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
