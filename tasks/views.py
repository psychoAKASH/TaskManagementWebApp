from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')


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
