from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm
from django.core.mail import send_mail
from django.contrib import messages
from .models import Task, Invitation
import uuid


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


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def send_invitation(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not Invitation.objects.filter(email=email).exists():
            token = uuid.uuid4().hex
            Invitation.objects.create(email=email, token=token, invited_by=request.user)
            # Send an email with the invitation link
            link = f"http://127.0.0.1:8000/register-with-invitation/?token={token}"
            send_mail(
                "You're invited!",
                f"Use this link to register: {link}",
                "admin@example.com",
                [email],
            )
            messages.success(request, "Invitation sent successfully!")
        else:
            messages.error(request, "This email has already been invited.")
    return render(request, "tasks/send_invitation.html")


def register_with_invitation(request):
    token = request.GET.get("token")
    invitation = Invitation.objects.filter(token=token, is_used=False).first()

    if not invitation:
        return render(request, "tasks/invalid_invitation.html")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password, email=invitation.email)
        invitation.is_used = True
        invitation.save()
        login(request, user)
        return redirect("/")

    return render(request, "tasks/register_with_invitation.html")
