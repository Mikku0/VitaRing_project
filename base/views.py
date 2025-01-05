from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomFrom, UserForm, MyUserCreationForm
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        messages.success(request, 'You are already logged in')
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or password is wrong')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in field '{field}': {error}")

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
    else:
        q = ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        messages = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomFrom()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomFrom(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host and not request.user.is_superuser:
        return HttpResponseForbidden('You are not allowed to do this.')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_superuser:
        return HttpResponseForbidden('You are not allowed to do this.')

    if request.method == 'POST':
        topic = room.topic
        room.delete()

        if not Room.objects.filter(topic=topic).exists():
            topic.delete()
            return redirect('home')
        else:
            return redirect('home')

    context = {
        'obj': room,
        'obj_type': type(room).__name__.lower()
    }
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user and not request.user.is_superuser:
        return HttpResponseForbidden('You are not allowed to do this.')

    if request.method == 'POST':
        message.delete()
        return redirect('home')  # dodać room/id zamiast home

    context = {
        'obj': message,
        'obj_type': type(message).__name__.lower()
    }
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    username = request.user.username
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        else:
            request.user.username = username
            messages.error(request, 'invalid data')

    return render(request, 'base/update-user.html', {'form': form})


def topics_page(request):
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
    else:
        q = ''
    topics_filtered = Topic.objects.filter(name__icontains=q)
    topics = topics_filtered.annotate(room_count=Count('room')).order_by('-room_count')

    return render(request, 'base/topics.html', {'topics': topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
