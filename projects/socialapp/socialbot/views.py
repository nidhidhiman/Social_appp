# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import  HttpResponse
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from socialapp.settings import BASE_DIR
from imgurpython import ImgurClient

# Create your views here.
#def execute(request):
 #   return HttpResponse("<h1>there start a projetct</h1>")

def sign_up(request):
    if request.method == "POST":
        #print("signup form submitted")
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #psw Siving the data into Db
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request,'success.html')
            #return redirect('login/')
    else:
        form = SignUpForm()
    #elif request.method == "GET":
     #   form = SignUpForm()
       # today=datetime.now()
    return render(request, 'index.html', {'form': form})

def log_in(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            #print username + password
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    #print 'valid user'
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = HttpResponseRedirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    #print 'invalid user'
                    response_data['message'] = 'Incorrect Password!'
    elif request.method == "GET":
            form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html',{'form':form})

def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request,'feed.html',{'posts': posts})
    else:
        return redirect('/login/')

def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None

def post_view(request):
    user=check_validation(request)
    if user:
        if request.method== "GET":
            form = PostForm()
            return render(request, 'post.html', {'form': form})
        elif request.method=="POST":
            form=PostForm(request.POST,request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')

                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                path=str(BASE_DIR +'/'+ post.image.url)
                client=ImgurClient("7c523b250772ade","5307069c8ab8398c385cfbeacd51857ed22")
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

        else:
            return redirect('/login/')
    return redirect('/feed/')

def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        print ('user is valid')
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id,user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id,user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user,post_id=post_id,comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')
