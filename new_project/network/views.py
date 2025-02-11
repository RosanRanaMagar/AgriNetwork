from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import *

from .models import *

def bubble_sort(posts):
    n = len(posts)
    for i in range(n):
        for j in range(0, n-i-1):
            if posts[j].date_created < posts[j+1].date_created:
                posts[j], posts[j+1] = posts[j+1], posts[j]
    return posts

def index(request):
   # all_posts = Post.objects.all().order_by('-date_created')
    all_posts = list(Post.objects.all())  # Convert queryset to list
    sorted_posts = bubble_sort(all_posts)  # Sort posts using bubble sort
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "page": "all_posts",
        'profile': False
    })


from django.contrib.auth.models import User
from .models import User 

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


"""
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(f"--------------------------Cover: {cover}----------------------------")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover           
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html") """
        
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from network.models import User, Follower

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        cover = request.FILES.get('cover')

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        # Check if passwords match
        if password != confirmation:
            return render(request, "network/register.html", {
                "password_error": "Passwords must match."
            })

        # Check if username is unique
        if User.objects.filter(username=username).exists():
            return render(request, "network/register.html", {
                "username_error": "Username is already taken."
            })
        
        # Check if email is unique
        if User.objects.filter(email=email).exists():
            return render(request, "network/register.html", {
                "email_error": "Email is already registered."
            })

        # Create new user if no errors
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = fname
            user.last_name = lname
            if profile:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            if cover:
                user.cover = cover
            user.save()

            # Create a Follower instance for the user
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "An error occurred during registration. Please try again."
            })

        # Log the user in and redirect to the homepage
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
    
    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
    })

def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following"
        })
    else:
        return HttpResponseRedirect(reverse('login'))

def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved"
        })
    else:
        return HttpResponseRedirect(reverse('login'))
        

"""
@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'") """

#linear search algorithm to keyword filtering for agriculture-related keywords
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post

# List of agriculture-related keywords
KEYWORDS = ['farm', 'harvest', 'agriculture', 'soil', 'crop', 'seed', 'plant', 'farmer', 'water', 'tractor', 'weather', 'green', 'grow', 'cultivate','beautiful','nature','landscape','sunset','sunrise','sky','clouds','mountain','river','lake','forest','tree','flower','grass','field','meadow','desert','beach','ocean','sea','island','city','town','village','building','architecture','house','home','road','street','bridge','tunnel','train','bus','car','bicycle','motorcycle','boat','ship','airplane','airport','station','port','park','garden','forest','tree','flower','grass','field']

def keyword_search(text, keywords):
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            return True
    return False

@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        video = request.FILES.get('video')  # Handle video uploads

         # Debugging: Check if video is received
        if video:
            print(f"Video received: {video.name}")

        if not text and not pic and not video:
            messages.error(request, "You must provide text, an image, or a video.")
            return redirect('index')  # Redirect to the desired page after error
        
        # Check if the text contains at least one agriculture-related keyword
        if text and not keyword_search(text, KEYWORDS):
                return HttpResponse("Your post must include at least one agriculture-related keyword: 'farm', 'harvest', 'soil', etc.")

        
        # Check image file type (allow only jpg, jpeg, png)
        if pic and not pic.name.endswith(('.jpg', '.jpeg', '.png')):
            messages.error(request, "Only images are supported (jpg, jpeg, png).")
            return redirect('index')
        # Check video file type (allow only mp4, avi, mov)
        if video and not video.name.endswith(('.mp4', '.avi', '.mov')):
            messages.error(request, "Only videos are supported (mp4, avi, mov).")
            return redirect('index')
        # If everything is validated, create the post
        
        try:
            Post.objects.create(creater=request.user, content_text=text, content_image=pic, content_video=video)
            messages.success(request, "Your post has been successfully created!")
            return HttpResponseRedirect(reverse('index'))  # Redirect to the desired page after success
        except Exception as e:
            return HttpResponse(f"Error while creating post: {e}")
    
    # If it's a GET request or validation fails, render the form again
    return HttpResponse("Your post must include at least one agriculture-related keyword: 'farm', 'harvest', 'soil', etc.")


"""    
import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post

# Example list of agriculture-related keywords in regular expression format
AGRICULTURE_KEYWORDS_REGEX = r'\b(farm\w*|harvest\w*|agriculture\w*|soil\w*|crop\w*|seed\w*|plant\w*|farmer\w*|water\w*|tractor\w*|weather\w*|green\w*|grow\w*|cultivat\w*)\b'

@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')

        # Check if text is empty
        if not text:
            messages.error(request, "Content cannot be empty.")
        
        # Regex filtering for agriculture-related keywords
        elif not re.search(AGRICULTURE_KEYWORDS_REGEX, text, re.IGNORECASE):  # Case-insensitive matching
            messages.error(
                request,
                f"Your post must include at least one agriculture-related keyword: 'farm', 'harvest', 'soil', etc."
            )
        
        # Check image file type (allow only jpg, jpeg, png)
        elif pic and not pic.name.endswith(('.jpg', '.jpeg', '.png')):
            messages.error(request, "Only images are supported (jpg, jpeg, png).")
        
        # If everything is validated, create the post
        else:
            try:
                Post.objects.create(creater=request.user, content_text=text, content_image=pic)
                messages.success(request, "Your post has been successfully created!")
                return HttpResponseRedirect(reverse('index'))  # Redirect to the desired page after success
            except Exception as e:
                return HttpResponse(f"Error while creating post: {e}")
    
    # If it's a GET request or validation fails, render the form again
    return HttpResponse("Your post must include at least one agriculture-related keyword: 'farm', 'harvest', 'soil', etc.")
"""

"""
@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            if(post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if(post.content_image):
                post_image = post.img_url()
            else:
                post_image = False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
            return HttpResponse("Method must be 'POST'")"""
            
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Post

# List of agriculture-related keywords
KEYWORDS = ['farm', 'harvest', 'agriculture', 'soil', 'crop', 'seed', 'plant', 'farmer', 'water', 'tractor', 'weather', 'green', 'grow', 'cultivate','beautiful','nature','landscape','sunset','sunrise','sky','clouds','mountain','river','lake','forest','tree','flower','grass','field','meadow','desert','beach','ocean','sea','island','city','town','village','building','architecture','house','home','road','street','bridge','tunnel','train','bus','car','bicycle','motorcycle','boat','ship','airplane','airport','station','port','park','garden','forest','tree','flower','grass','field']

def keyword_search(text, keywords):
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            return True
    return False

@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        video = request.FILES.get('video')
        img_chg = request.POST.get('img_change')
        vid_chg = request.POST.get('vid_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)

        # Check if the text contains at least one agriculture-related keyword
        if text and not keyword_search(text, KEYWORDS):
            return JsonResponse({
                "success": False,
                "error": "Your post must include at least one agriculture-related keyword: 'farm', 'harvest', 'soil', etc."
            })

        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            if vid_chg != 'false':
                post.content_video = video
            post.save()
            
            post_text = post.content_text if post.content_text else False
            post_image = post.img_url() if post.content_image else False
            post_video = post.content_video.url if post.content_video else False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image,
                "video": post_video
            })
        except Exception as e:
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
        return HttpResponse("Method must be 'POST'")

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Follower: {request.user}......................")
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Unfollower: {request.user}......................")
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(post=post,commenter=request.user,comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)
    
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse

@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Get the current logged-in user
        user = request.user
        
        # Get data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')
        cover_picture = request.FILES.get('cover_picture')
        
        # Update fields if data is provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if username:
            user.username = username
        if bio:
            user.bio = bio
        if profile_picture:
            user.profile_pic = profile_picture
        if cover_picture:
            user.cover = cover_picture
        
        # Save the changes to the user profile
        user.save()

        # Redirect to the updated profile page using reverse()
        return redirect(reverse('profile', kwargs={'username': user.username}))

    # Render the profile edit form
    return render(request, "network/profile_edit.html")




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import User

@login_required
def delete_profile_picture(request):
    user = request.user
    if user.profile_pic:
        user.profile_pic.delete()  # Deletes the file from storage
        user.profile_pic = None  # Clears the field in the database
        user.save()
    return redirect('profile')  # Redirect to the appropriate view

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_cover_picture(request):
    user = request.user
    if user.cover:
        user.cover.delete()  # Deletes the file from storage
        user.cover = None  # Clears the field in the database
        user.save()
    return redirect('profile')  # Redirect to the profile page or an appropriate view


def quiz_view(request):
    return render(request, 'network/quiz.html')



# filepath: /c:/7th semester/new_project/network/views.py
from django.shortcuts import render
from .weather_service import get_weather

def weather_view(request):
    city = request.GET.get('city', 'Kathmandu')  # Default city
    weather_data = get_weather(city)
    return render(request, 'weather.html', {'weather_data': weather_data, 'city': city})