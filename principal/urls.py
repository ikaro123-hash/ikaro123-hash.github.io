from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'principal'

urlpatterns = [
    path('', views.home, name='home'),  # <- ROTA VAZIA (ROOT)
    path('login/', views.login_view, name='login'),
    path('aluno/', views.aluno_redirect, name='aluno_redirect'),
    path('aluno/<int:aluno_id>/', views.menu_aluno, name='menu_aluno_com_id'),
    path('home/', views.home, name='home'),
    path('admin-menu/', views.menu_admin, name='menu_admin'),
    path('painel/alunos/', views.listar_alunos, name='listar_alunos'),
    path('painel/alunos/novo/', views.criar_aluno, name='criar_aluno'),
    path('painel/alunos/<int:aluno_id>/editar/', views.editar_aluno, name='editar_aluno'),
    path('painel/alunos/<int:aluno_id>/excluir/', views.excluir_aluno, name='excluir_aluno'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('meus-dados/', views.meus_dados, name='meus_dados'),
    path('historico/', views.historico_view, name='historico'),

   
    
]

