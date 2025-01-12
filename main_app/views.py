from django.shortcuts import render, redirect
from .models import Post, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import uuid
import boto3

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'catcollector-sb'

# Define the home view
def home(request):
  return render(request, 'home.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def posts_index(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'posts/index.html', { 'posts': posts })

@login_required
def posts_detail(request, post_id):
  post = Post.objects.get(id=post_id)
  return render(request, 'posts/detail.html', { 'post': post })

@login_required
def add_photo(request, post_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            photo = Photo(url=url, post_id=post_id)
            photo.save()
        except:
            print('An error occurred uploading file to S3')
    return redirect('detail', post_id=post_id)


def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)



class PostCreate(LoginRequiredMixin, CreateView):
  model = Post
  fields = ['title', 'content', 'description', 'tags']

  def form_valid(self, form):
    form.instance.user = self.request.user  # form.instance is the cat
    return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, UpdateView):
  model = Post
  fields = '__all__'

class PostDelete(LoginRequiredMixin, DeleteView):
  model = Post
  success_url = '/posts/'