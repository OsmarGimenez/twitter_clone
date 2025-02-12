from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Relationship,Profile
from django.contrib.auth import login
from .forms import UserRegisterForm, PostForm, UserUpdateForm, ProfileUpdateForm, SearchForm
from django.contrib.auth.models import User
from django.http import Http404
from django.urls import NoReverseMatch, reverse
from django.db.models import Exists, OuterRef

@login_required
def home(request):
    posts = Post.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    # Obtener usuarios que no sigo y que no son el usuario actual
    suggested_users = User.objects.exclude(
        Exists(Relationship.objects.filter(
            from_user=request.user,
            to_user=OuterRef('pk')
        ))
    ).exclude(pk=request.user.pk)[:3]

    # Serializar los datos de usuario, incluyendo la URL de la foto de perfil
    serialized_users = []
    for user in suggested_users:
        serialized_user = {
            'username': user.username,
            'profile_image': user.profile.image.url if hasattr(user, 'profile') and user.profile.image else '/static/default.png'  # URL de la imagen o imagen por defecto
        }
        serialized_users.append(serialized_user)

    context = {
        'posts': posts,
        'form': form,
        'suggested_users': serialized_users  # Pasar los usuarios serializados al template
    }
    return render(request, 'twitter/newsfeed.html', context)
def register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        p_form = ProfileUpdateForm(request.POST, request.FILES)

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()

            profile = p_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)
            return redirect('login')

        else:
            # Los errores se mostrarán en el formulario automáticamente
            pass  # No es necesario hacer nada aquí

    else:
        u_form = UserRegisterForm()
        p_form = ProfileUpdateForm()

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, 'twitter/register.html', context)
	

def delete(request, post_id):
	post = Post.objects.get(id=post_id)
	post.delete()
	return redirect('home')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.posts.all()

    # Define el tipo de lista a mostrar (puedes pasar esto como un parámetro en la URL si lo deseas)
    list_type = request.GET.get('list_type', None)  # Obtiene el valor del parámetro 'list_type' de la URL

    context = {
        'user': user,
        'profile': profile,
        'posts': posts,
        'list_type': list_type,  # Añade el tipo de lista al contexto
    }
    return render(request, 'twitter/profile.html', context)

@login_required
def editar(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			return redirect('home')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm()

	context = {'u_form' : u_form, 'p_form' : p_form}
	return render(request, 'twitter/editar.html', context)

@login_required
def follow(request, username):
    current_user = request.user
    to_user = get_object_or_404(User, username=username)
    Relationship.objects.create(from_user=current_user, to_user=to_user)
    return redirect('profile', username=username)

@login_required
def unfollow(request, username):
    current_user = request.user
    to_user = get_object_or_404(User, username=username)
    Relationship.objects.filter(from_user=current_user, to_user=to_user).delete()
    return redirect('profile', username=username)

def search_users(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Filtrar usuarios que contienen el término de búsqueda en su nombre de usuario
            results = User.objects.filter(username__icontains=query).exclude(username=request.user.username)
            # Obtener usuarios que el usuario actual sigue
            following = [rel.to_user for rel in Relationship.objects.filter(from_user=request.user)]
            return render(request, 'twitter/search_results.html', {'form': form, 'results': results, 'following': following})
    else:
        form = SearchForm()
    return render(request, 'twitter/search_results.html', {'form': form})

@login_required

def user_list(request, username=None, list_type=None):  # username es opcional
    if username:  # Se proporciona un username, mostramos la lista de otro usuario
        user = get_object_or_404(User, username=username)
        profile = user.profile  # Acceder al perfil del usuario
    else:  # No se proporciona username, mostramos la lista del usuario logueado
        try:
            user = request.user  # Usamos request.user directamente
            profile = request.user.profile  # Acceder al perfil del usuario logueado
        except AttributeError:  # Si el usuario no está logueado o no tiene perfil, redirige al login o a la creación de perfil
            return redirect('login') # o redirect('create_profile') si tienes una vista para crear perfiles

    if not list_type:  # Si no se especifica el tipo de lista, redirigir a la página de perfil
        return redirect('profile', username=user.username)

    if list_type == 'followers':
        title = 'Seguidores'
        users = profile.followers().all()  # Llama a la función y luego usa .all()
    elif list_type == 'following':
        title = 'Seguidos'
        users = profile.following().all()  # Llama a la función y luego usa .all()
    else:
        raise Http404

    # Los siguientes conjuntos solo se calculan si es el usuario logueado
    if user == request.user:
        following = set(profile.following().values_list('user_id', flat=True))  # Llama a la función
        followers = set(profile.followers().values_list('user_id', flat=True))  # Llama a la función
    else:
        following = set()
        followers = set()

    context = {
        'title': title,
        'users': users,
        'following': following,
        'followers': followers,
        'profile_user': user if username else None,  # Pasamos el usuario de perfil si existe
        'list_type': list_type
    }

    return render(request, 'twitter/user_list.html', context)

