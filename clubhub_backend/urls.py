from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API routes
    path('api/', include('api.urls')),

    # Rendered page routes (reuse existing templates)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login_page', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('about_page', TemplateView.as_view(template_name='about.html'), name='about_page'),
    path('contact_page', TemplateView.as_view(template_name='home.html'), name='contact_page'),
    path('explore_clubs_page', TemplateView.as_view(template_name='explore_clubs.html'), name='explore_clubs_page'),
    path('people_page', TemplateView.as_view(template_name='people.html'), name='people_page'),
    path('account_page', TemplateView.as_view(template_name='account.html'), name='account_page'),
    path('create_account_page', TemplateView.as_view(template_name='create_account.html'), name='create_account_page'),
    path('clubpage_page', TemplateView.as_view(template_name='clubpage.html'), name='clubpage_page'),
    path('myclubs_page', TemplateView.as_view(template_name='myclubs.html'), name='myclubs_page'),
] 