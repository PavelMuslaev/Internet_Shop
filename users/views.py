from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse

from main.models import Product

from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser


def register(request: HttpRequest) -> HttpResponseBase:
    """Create a new user account and log the user in after registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponseBase:
    """Authenticate a user by email and start a session."""
    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required(login_url='/users/login')
def profile_view(request: HttpRequest) -> HttpResponseBase:
    """Render and update the current user's profile page."""
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    recommended_products = Product.objects.all().order_by('id')[:3]

    return TemplateResponse(
        request,
        'users/profile.html',
        {
            'form': form,
            'user': request.user,
            'recommended_products': recommended_products,
        },
    )


@login_required(login_url='/users/login')
def account_details(request: HttpRequest) -> TemplateResponse:
    """Render the account details profile partial."""
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(
        request,
        'users/partials/account_details.html',
        {'user': user},
    )


@login_required(login_url='/users/login')
def edit_account_details(request: HttpRequest) -> TemplateResponse:
    """Render the editable account details profile partial."""
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(
        request,
        'users/partials/edit_account_details.html',
        {'user': request.user, 'form': form},
    )


@login_required(login_url='/users/login')
def update_account_details(request: HttpRequest) -> HttpResponseBase:
    """Update account details and return the appropriate profile partial."""
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            return TemplateResponse(
                request,
                'users/partials/account_details.html',
                {'user': updated_user},
            )
        return TemplateResponse(
            request,
            'users/partials/edit_account_details.html',
            {'user': request.user, 'form': form},
        )
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
    return redirect('users:profile')


def logout_view(request: HttpRequest) -> HttpResponseBase:
    """End the current user session and redirect to the home page."""
    auth_logout(request)
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('main:index')})
    return redirect('main:index')
