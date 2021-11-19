from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

#Login Page
class CustomLoginView(LoginView):
    template_name = 'todolist/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
#send User to the Tasks Page when they log in and see the list items
    def get_success_url(self):
        return reverse_lazy('tasks')

#RegisterPage
class RegisterPage(FormView):
    template_name = 'todolist/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        #if User is created successfully, use login function
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)



# Tasks Page -> LoginRequiredMixin (User Restriction) is a built in function from django that prevents changes, if not logged in as User
# so a User cant go via the Browser to f.ex. "Tasks" without being logged in, he will be redirected to the login Page
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
# function for filtering the tasks to assign to the logged in User, so only the User can see his tasks, but not the one from other Users
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)

        context['search_input'] = search_input

        return context

#Details = Task List
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'todolist/task.html'
# Create a new Task
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        #make sure its the logged in User
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
# update View
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')
# delete View
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name='task'
    success_url = reverse_lazy('tasks')

