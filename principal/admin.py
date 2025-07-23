from django.contrib import admin
from .models import Aluno, ListaDia, Presenca, Admin

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
     list_display = ('nome', 'matricula', 'curso', 'email', 'user')
     search_fields = ('nome', 'matricula', 'email', 'user__username')

@admin.register(ListaDia)
class ListaDiaAdmin(admin.ModelAdmin):
    list_display = ['data', 'aberta']

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'lista', 'confirmado_em']

    admin.site.register(Admin)
