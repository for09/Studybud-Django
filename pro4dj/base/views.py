from django.shortcuts import render, redirect
from django.db.models import Q 
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login ,logout 
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm,UserForm


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user =User.objects.get(username = username)
        except:
            messages.error(request,'user dosen\'t exists')
            return redirect('login')
        user = authenticate(request,username = username,password = password )

        if user is not None:
            login(request, user) 
            return redirect('home')
        else:
            messages.error(request,'username or password dosen\'t exists')

    context = {'page': page }
    return render(request,'base/login_register.html' , context)


def logoutUser(request):
    logout(request)
    return redirect('home')



def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home') 
        else:
            messages.error(request,'An error occured during registration')
    return render(request, 'base/login_register.html',{'form' : form})



###################
def home(request):
    # get()method called on GET attribute of request object when user submits a query parameter in form with method set to 'GET'  


    q = request.GET.get('q') if request.GET.get('q')!= None else ''
   
   #? 
    rooms = Room.objects.filter(Q(topic__name__icontains = q) | Q(name__icontains = q) | Q(description__icontains = q))

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms' : rooms,'topics' : topics,'room_count' : room_count, 'room_messages' : room_messages}
    
    return render(request, 'base/home.html',context)

####################


def room(request,pk):

    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    if request.method == "POST":
        message = Message.objects.create(
            user  = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        
        return redirect('room',pk = room.id)
    
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user,'rooms' : rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url = '/login')
def createRoom(request):
    # creating black form
    form  = RoomForm()
    topics = Topic.objects.all()
    # if the request is "POST" populate the form (fill the form) with the data contained in that request (request.POST)
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name=request.POST.get('name'),
            description=request.POST.get('decription'),
        )

        #form = RoomForm(request.POST)
        # validate the form if it is valid save the contents of form into the database
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            # redirect the user to another page("HOME") which is stored with vertain name in URLPATTERNS = [paths .. name = NAME("HOME")
            #  path..] in urls.py 
            
        return redirect('home')
    context = {'form' : form,'topics' :topics,'room':room}
    return render(request,'base/room_form.html',context)



@login_required(login_url = '/login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('u r not allowed here')
    

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        # form = RoomForm(request.POST,instance=room)
        # if form.is_valid():
        form.save()
        return redirect('home')
        
    # context is basically context data for the template which will be renderd by the view
    # take form(key in dictionary) variable which will be accesed by template to access the data in the form (value in dictionary)      
    
    context = {'form' : form,'topics' :topics,'room':room}
    return render(request,'base/room_form.html',context)



@login_required(login_url = '/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse('u r not allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html',{'obj':room})



@login_required(login_url = '/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)

    if request.user != message.user:
        return HttpResponse('u r not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html',{'obj' : message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})

def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''

    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics': topics})



def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages' : room_messages })