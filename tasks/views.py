from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm



@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)  # Only show tasks of the logged-in user
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # Associate the task with the logged-in user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)  # Ensure the task belongs to the user
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)  # Ensure the task belongs to the user
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('task_list')  # Redirect to the task list
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
