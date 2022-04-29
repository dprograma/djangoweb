from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from . models import Topic, Room, Message
from django.contrib.auth.forms import UserCreationForm
from .forms import RoomForm

# Create your views here.

def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
      return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)
    
def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
      form = UserCreationForm(request.POST)
      if form.is_valid:
        user = form.save(commit=False)
        user.username = user.username.lower()
        user.save()
        login(request, user)
        return redirect('home')
      else:
        messages.error("Something went wrong during registration.")
    context = {'form':form}
    return render(request, 'base/login_register.html', context)
      
      
def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    print("q is: ", q)
    rooms = Room.objects.filter(Q(topic__name__icontains=q)|
    Q(name__icontains=q)| Q(description__icontains=q) | Q(host__username__icontains=q))
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    print("room is: ", rooms.query)
    print("room queryset", rooms)
    room_count = rooms.count()
    print("room count", room_count)
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
      Message.objects.create(
        user = request.user,
        room = room,
        body = request.POST.get('body')
        )
      room.participants.add(request.user)
      return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)
    
    
@login_required(login_url='login')
def userProfile(request, pk):
  user = User.objects.get(id=pk)
  topics = Topic.objects.all()
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  
  context = {'user': user, 'topics': topics, 'rooms': rooms, 'room_messages': room_messages}
  return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
      messages.error(request, 'You are not allowed in this room.')
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
      messages.error('You are not allowed to delete this room.')
    if request.method == "POST":
        room.delete() 
        return redirect('home')
    context = {'obj':room}
    return render(request, 'base/delete.html', context)
    
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
      messages.error('You are not allowed to delete this room.')
    if request.method == "POST":
        message.delete() 
        return redirect('home')
    context = {'obj':message}
    return render(request, 'base/delete.html', context)