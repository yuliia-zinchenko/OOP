from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from .forms import RegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user=user)
            return redirect('book_main')
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('book_main')

    
    def form_valid(self, form):
        user = form.save() 
        login(self.request, user)  
        return super().form_valid(form)
    

def profile_settings(request):
    return render(request, 'users/profile.html')





@login_required
def profile_settings(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save() 
        return redirect('profile_settings')

    return render(request, 'users/profile.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })




