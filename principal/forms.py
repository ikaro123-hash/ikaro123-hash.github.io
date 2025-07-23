from django import forms
from django.contrib.auth.models import User
from .models import Aluno

class AlunoForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    matricula = forms.CharField(max_length=20)
    curso = forms.CharField(max_length=100)

    class Meta:
        model = Aluno
        fields = ['nome']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Esse nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Aluno.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data['matricula']
        if Aluno.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError("Essa matrícula já está cadastrada.")
        return matricula

    def save(self, commit=True):
        # Cria o usuário
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
        )
        user.save()

        # Cria o aluno vinculado
        aluno = super().save(commit=False)
        aluno.user = user
        aluno.email = self.cleaned_data['email']
        aluno.matricula = self.cleaned_data['matricula']
        aluno.curso = self.cleaned_data['curso']

        if commit:
            aluno.save()
        return aluno
