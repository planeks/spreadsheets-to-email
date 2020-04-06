from django.urls import path, include
from .views import create_template, template_list, edit_template, delete_template

app_name = 'email_templates'

urlpatterns = [
    path('', template_list, name='template_list'),
    path('create/', create_template, name='create_template'),
    path('<int:pk>/edit/', edit_template, name='edit_template'),
    path('<int:pk>/delete/', delete_template, name='delete_template')
]
