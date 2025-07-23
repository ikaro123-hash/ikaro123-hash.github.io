from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def clean(self):
        if self.user.is_staff or self.user.is_superuser:
            raise ValidationError("Admins não podem ser vinculados como alunos.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
    
class Admin(models.Model):  # Pode chamar de AdminSistema se quiser
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f'Administrador: {self.nome}'

class ListaDia(models.Model):
    TURNO_CHOICES = [
        ('12h', '12 horas'),
        ('18h', '18 horas'),
    ]

    data = models.DateField(default=timezone.now)
    turno = models.CharField(max_length=3, choices=TURNO_CHOICES)
    aberta = models.BooleanField(default=True)

    class Meta:
        unique_together = ('data', 'turno')

    def __str__(self):
        return f'Lista {self.data.strftime("%d/%m/%Y")} - {self.get_turno_display()} - {"Aberta" if self.aberta else "Fechada"}'

class Presenca(models.Model):
    lista = models.ForeignKey(ListaDia, on_delete=models.CASCADE, related_name='presencas')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    confirmado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lista', 'aluno')
        ordering = ['confirmado_em']

    def posicao(self):
        presencas = Presenca.objects.filter(lista=self.lista).order_by('confirmado_em').values_list('id', flat=True)
        try:
            return list(presencas).index(self.id) + 1
        except ValueError:
            return None