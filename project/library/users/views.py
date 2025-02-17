from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, PasswordResetForm, SetPasswordForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.query_utils import Q
from book.models import UserBook
from movie.models import Movie
from TVshow.models import TVshow

def user_not_authenticated(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login')) 
        return function(request, *args, **kwargs)
    return wrap

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect('login')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("users/activate_account.html",{
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        pass
    else: 
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly')
        
from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login') 


def user_login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        user = None

        if '@' in username_or_email: 
            try:
                user = get_user_model().objects.get(email=username_or_email)
            except get_user_model().DoesNotExist:
                user = None
        else:
            try:
                user = get_user_model().objects.get(username=username_or_email)
            except get_user_model().DoesNotExist:
                user = None
        if user and user.check_password(password):
            login(request, user)
            return redirect('book_main')
        else:
            messages.error(request, 'Invalid username or password')
            form = AuthenticationForm() 
            return render(request, 'users/login.html', {'form': form})

    form = AuthenticationForm() 
    return render(request, 'users/login.html', {'form': form})




def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if get_user_model().objects.filter(email=email).exists():
                form.add_error('email', "An account with this email already exists.")
                return render(request, "users/register.html", {"form": form})
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            activateEmail(request, user, email) 
            request.session['username'] = user.username
            request.session['email'] = user.email
            return redirect('registration_success')
        else:
            messages.error(request, ' ')
            return render(request, "users/register.html", {"form": form})
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def registration_success(request):
    username = request.session.pop('username', None)  
    email = request.session.pop('email', None)  
    return render(request, 'users/registration_success.html', {'username':username, 'email':email})


@login_required
def profile_settings(request):
    books_read_count = UserBook.objects.filter(user=request.user, status='mark_as_read').count()
    movies_watched_count = Movie.objects.filter(user=request.user, status='mark_as_watched').count()
    shows_watched_count = TVshow.objects.filter(user=request.user, status='mark_as_watched').count()


    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save() 
            return redirect('profile_settings')
        else:
            return render(request, 'users/profile.html', {
                'form': form,
                'books_read_count': books_read_count, 
                'movies_watched_count': movies_watched_count,
                'shows_watched_count': shows_watched_count,
            })

    else:
        form = ProfileUpdateForm(instance=request.user)
        return render(request, 'users/profile.html', {
            'form': form,
            'books_read_count': books_read_count,
            'movies_watched_count': movies_watched_count,
            'shows_watched_count': shows_watched_count,
        })
    


@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user_email = form.cleaned_data['email']
                associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
                if associated_user:
                    subject = "Password Reset request"
                    message = render_to_string("users/template_reset_password.html",{
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                     })
                    email = EmailMessage(subject, message, to=[associated_user.email])
                    if email.send():
                        messages.success(request, 
                        """
                        <h2>Password reset sent</h2>
                        <p>
                        We've emailed you instructions for setting your password, if an account exists with the email you entered.
                        You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder.
                        </p>
                        """
                        )
                    else:
                        messages.error(request, "Problem sending reset password email")
                    
                return redirect('login')

    form = PasswordResetForm()
    return render(
        request=request,
        template_name="users/password_reset.html",
        context={"form":form}
    )

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in</b> now.")
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form':form})
    else:
        messages.error(request, "Link is expired!")
    messages.error(request, 'Something went wrong')
    return redirect('login')




