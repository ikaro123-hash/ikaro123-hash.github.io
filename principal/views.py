from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Aluno, ListaDia, Presenca, User
from django.contrib.auth import authenticate, login
from datetime import date
from .forms import AlunoForm

# Verifica se o usuário tem um perfil de administrador vinculado
def is_admin(user):
    return hasattr(user, 'admin')

@login_required
def menu_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    hoje = date.today()
    turnos = ['12h', '18h']
    max_usuarios = 50

    listas = {}

    for turno in turnos:
        lista, _ = ListaDia.objects.get_or_create(data=hoje, turno=turno)
        presencas = lista.presencas.select_related('aluno').order_by('confirmado_em')
        total_confirmados = presencas.count()
        
        presenca = presencas.filter(aluno=aluno).first()

        posicao = None
        if presenca:
            # Encontra a posição do aluno na lista (começando em 1)
            for idx, p in enumerate(presencas, start=1):
                if p.id == presenca.id:
                    posicao = idx
                    break
        
        listas[turno] = {
            'lista': lista,
            'presencas': presencas,
            'total_confirmados': total_confirmados,
            'presenca': presenca,
            'posicao': posicao,
        }

    if request.method == 'POST':
        turno = request.POST.get('turno')
        if turno not in turnos:
            messages.error(request, 'Turno inválido.')
            return redirect('principal:menu_aluno_com_id', aluno_id=aluno_id)

        lista = ListaDia.objects.get(data=hoje, turno=turno)
        presenca = lista.presencas.filter(aluno=aluno).first()

        if 'confirmar' in request.POST:
            if lista.aberta and not presenca and lista.presencas.count() < max_usuarios:
                Presenca.objects.create(aluno=aluno, lista=lista)
                messages.success(request, f'Presença confirmada na lista das {turno}!')
            else:
                messages.error(request, 'Não foi possível confirmar a presença.')

        elif 'remover' in request.POST:
            if presenca:
                presenca.delete()
                messages.success(request, f'Presença removida da lista das {turno}.')
            else:
                messages.warning(request, 'Você não está na lista para remover.')

        return redirect('principal:menu_aluno_com_id', aluno_id=aluno_id)

    return render(request, 'principal/menu_aluno.html', {
        'listas': listas,
        'data_hoje': hoje,
        'max_usuarios': max_usuarios,
        'aluno': aluno,
    })

@login_required
@user_passes_test(is_admin)
def menu_admin(request):
    hoje = date.today()
    turnos = ['12h', '18h']
    max_usuarios = 50

    listas = []
    for turno in turnos:
        lista, _ = ListaDia.objects.get_or_create(data=hoje, turno=turno)
        presencas = lista.presencas.select_related('aluno').order_by('confirmado_em')
        total_confirmados = presencas.count()
        listas.append({
            'lista': lista,
            'presencas': presencas,
            'total_confirmados': total_confirmados,
        })

    if request.method == 'POST':
        turno = request.POST.get('turno')
        if turno not in turnos:
            messages.error(request, 'Turno inválido.')
            return redirect('principal:menu_admin')

        lista = ListaDia.objects.get(data=hoje, turno=turno)

        if 'abrir' in request.POST:
            lista.aberta = True
            lista.save()
            messages.success(request, f'Lista do turno {lista.get_turno_display()} aberta.')
        elif 'fechar' in request.POST:
            lista.aberta = False
            lista.save()
            messages.success(request, f'Lista do turno {lista.get_turno_display()} fechada.')

        return redirect('principal:menu_admin')

    return render(request, 'principal/lista.html', {
        'listas': listas,
        'max_usuarios': max_usuarios,
    })

@login_required
@user_passes_test(is_admin)
def listar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'principal/listar_alunos.html', {'alunos': alunos})

@login_required
@user_passes_test(is_admin)
def criar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            username = form.cleaned_data['username']
            senha = form.cleaned_data['password']
            email = form.cleaned_data['email']
            matricula = form.cleaned_data['matricula']
            curso = form.cleaned_data['curso']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Este nome de usuário já existe.")
                return redirect('principal:criar_aluno')

            if Aluno.objects.filter(email=email).exists():
                messages.error(request, "Este e-mail já está cadastrado.")
                return redirect('principal:criar_aluno')

            if Aluno.objects.filter(matricula=matricula).exists():
                messages.error(request, "Esta matrícula já está cadastrada.")
                return redirect('principal:criar_aluno')

            user = User.objects.create_user(username=username, password=senha, email=email)
            user.is_staff = False
            user.save()

            aluno = Aluno.objects.create(
                user=user,
                nome=nome,
                email=email,
                matricula=matricula,
                curso=curso
            )

            messages.success(request, f'Aluno {aluno.nome} criado com sucesso.')
            return redirect('principal:listar_alunos')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = AlunoForm()

    return render(request, 'principal/criar_aluno.html', {'form': form})




@login_required
@user_passes_test(is_admin)
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno atualizado com sucesso!')
            return redirect('listar_alunos')
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'principal/form_aluno.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def excluir_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        # Se você quiser apagar o usuário vinculado, descomente a próxima linha
        # aluno.user.delete()
        aluno.delete()
        messages.success(request, 'Aluno excluído com sucesso!')
        return redirect('listar_alunos')
    return render(request, 'principal/confirma_exclusao.html', {'aluno': aluno})

@login_required
def home(request):
    return render(request, 'principal/base.html')

@login_required
def aluno_redirect(request):
    if hasattr(request.user, 'aluno'):
        return redirect('principal:menu_aluno_com_id', aluno_id=request.user.aluno.id)
    else:
        messages.error(request, 'Este usuário não está vinculado a um aluno.')
        return redirect('login')




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'aluno'):
                return redirect('principal:menu_aluno_com_id', aluno_id=user.aluno.id)
            elif user.is_staff or user.is_superuser:
                return redirect('principal:menu_admin')  # ajuste conforme sua URL
            else:
                messages.warning(request, 'Usuário autenticado, mas sem perfil definido.')
                return redirect('login')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'principal/registration/login.html')

    return render(request, 'principal/registration/login.html')

def meus_dados(request):
    if hasattr(request.user, 'aluno'):
        aluno = request.user.aluno
        return render(request, 'principal/meus_dados.html', {'aluno': aluno})
    else:
        messages.error(request, 'Você não está vinculado a um aluno.')
        return redirect('login')
    
def historico_view(request):
    try:
        aluno = request.user.aluno
        presencas = Presenca.objects.select_related('lista').filter(aluno=aluno)
    except:
        presencas = []

    return render(request, 'principal/historico.html', {'presencas': presencas})
    