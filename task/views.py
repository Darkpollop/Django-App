from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone



def home(request):
    return render(request,'home.html')
    
def signup(request):
    
    if request.method =='GET':
        return render(request,'signup.html',{
        'form': UserCreationForm
    })
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('task')
            except IntegrityError:
                return render(request,'signup.html',{
                    'form': UserCreationForm,
                    "error" : 'Username already exist'
                 })
            
        return render(request,'signup.html',{
            'form': UserCreationForm,
            "error" : 'Contraseña no coinciden'
                 })

@login_required
def task(request):
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=True)
    return render (request, 'task.html',{'tasks': tasks})

@login_required
def task_completed(request):
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=False).order_by('-datecomplete')
    return render (request, 'task.html',{'tasks': tasks})

@login_required
def create_task(request):
    if request.method =='GET':
        return render(request, 'create_task.html', {
            'form' : TaskForm
    })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request, 'create_task.html', {
            'form' : TaskForm,
            'error' : 'por favor indicar datos validos'
            })

@login_required   
def signout(request):
    logout(request)
    return redirect("home")

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('task')

@login_required
def task_detail(request, task_id):
    if request.method =='GET':
        task = get_object_or_404(Task, pk=task_id,  user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id,  user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('task')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': "error updating task"})
 
@login_required    
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method =='POST':
        task.datecomplete = timezone.now()
        task.save()
        return redirect('task')

@login_required 
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method =='POST':
        task.delete()
        return redirect('task') 


            