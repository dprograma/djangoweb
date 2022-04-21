from django.shortcuts import redirect, render
from django.db.models import Q
from . models import Topic, Room, Message
from .forms import RoomForm

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'learn python with me'},
#     {'id': 2, 'name': 'lets learn JavaScript'},
#     {'id': 3, 'name': 'frontend development'},
# ]


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    print("q is: ", q)
    rooms = Room.objects.filter(Q(topic__name__icontains=q)|
    Q(name__icontains=q)| Q(description__icontains=q)| Q(topic__host__icontains=q))
    print("room is: ", rooms.query)
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)

def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)     
    if request.method == "POST":
        room.delete() 
        return redirect('home')
    context = {'obj':room}
    return render(request, 'base/delete.html', context)