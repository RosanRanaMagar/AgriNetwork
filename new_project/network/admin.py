
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

def quick_sort_users(users):
    if len(users) <= 1:
        return users
    else:
        pivot = users[0]
        less_than_pivot = [user for user in users[1:] if user.profile_pic and pivot.profile_pic]
        greater_than_pivot = [user for user in users[1:] if not user.profile_pic or not pivot.profile_pic]
        return quick_sort_users(less_than_pivot) + [pivot] + quick_sort_users(greater_than_pivot)

class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the list view
    list_display = ('username','profile_picture', 'email', 'first_name', 'last_name', 'date_joined')
    
    # Add search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Add sorting by username in ascending order
    ordering = ('first_name',)  # You can also use 'last_name' or 'username' if needed

    # Custom method to display the user's profile picture
    def profile_picture(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.profile_pic.url)
        return "No Image"
    profile_picture.short_description = 'Profile Picture'

    # Override get_queryset to use quick sort
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        users = list(queryset)
        sorted_users = quick_sort_users(users)
        
        # Create a list of IDs in the sorted order
        sorted_ids = [user.id for user in sorted_users]
        
        # Use Case/When to preserve the order in the queryset
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])
        return queryset.filter(pk__in=sorted_ids).order_by(preserved_order)

# Register your custom UserAdmin
admin.site.register(User, CustomUserAdmin)



from django.contrib import admin
from django.utils.html import format_html
from .models import Post

class PostAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('creater', 'content_text', 'content_image','display_video', 'date_created', 'comment_count')
    
    # Enable filtering by user and creation date
    list_filter = ('creater', 'date_created')
    
    # Set default ordering by creation date (descending order)
    ordering = ('-date_created',)
    
    # Add search functionality for posts
    search_fields = ('content_text', 'creater__username')  # Search by text or creator's username

    # Customize the admin form to display fields in a structured way
    fieldsets = (
        ('Post Details', {
            'fields': ('creater', 'content_text', 'content_image','content_video')
        }),
        ('Statistics', {
            'fields': ('date_created', 'comment_count', 'likers', 'savers')
        }),
    )
    
    # Custom method to display the posted video
    def display_video(self, obj):
        if obj.content_video:
            return format_html('<video width="230" height="150" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>', obj.content_video.url)
        return "No Video"
    display_video.short_description = 'Posted Video'

admin.site.register(Post, PostAdmin)


"""
from django.contrib import admin
from .models import Comment

class CommentAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view
    list_display = ('id', 'post', 'commenter', 'comment_content', 'comment_time')
    
    # Add search functionality
    search_fields = ('comment_content', 'commenter__username', 'post__content_text')
    
    # Add filters for specific fields
    list_filter = ('comment_time', 'post')
    
    # Sort comments by creation time in descending order (most recent first)
    ordering = ('-comment_time',)
    
    # Make fields readonly (e.g., for audit purposes)
    readonly_fields = ('comment_time',)

    # Optional: Customize the detail view for comments
    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'commenter', 'comment_content', 'comment_time'),
        }),
    )

# Register the Comment model with the custom CommentAdmin
admin.site.register(Comment, CommentAdmin) """

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Case, When
from .models import Comment, Post

def bubble_sort_comments(comments):
    n = len(comments)
    for i in range(n):
        for j in range(0, n-i-1):
            if len(comments[j].comment_content) > len(comments[j+1].comment_content):
                comments[j], comments[j+1] = comments[j+1], comments[j]
    return comments

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'commenter', 'comment_content', 'comment_time','post_image','display_video')
    search_fields = ('comment_content', 'commenter__username', 'post__content_text')
    list_filter = ('comment_time', 'post')
    ordering = ('-comment_time',)
    readonly_fields = ('comment_time',)
    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'commenter', 'comment_content', 'comment_time'),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        comments = list(queryset)
        sorted_comments = bubble_sort_comments(comments)
        
        # Create a list of IDs in the sorted order
        sorted_ids = [comment.id for comment in sorted_comments]
        
        # Use Case/When to preserve the order in the queryset
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])
        return queryset.filter(pk__in=sorted_ids).order_by(preserved_order)
    
    def post_image(self, obj):
        if obj.post.content_image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.post.content_image.url)
        return "No Image"
    
    def display_video(self, obj):
        if obj.post.content_video:
            return format_html('<video width="230" height="150" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>', obj.post.content_video.url)
        return "No Video"
    display_video.short_description = 'Post Video'

    post_image.short_description = 'Post Image'

admin.site.register(Comment, CommentAdmin)


"""
from django.contrib import admin
from .models import Follower

class FollowerAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'user', 'follower_count')
    
    # Add search functionality
    search_fields = ('user__username', 'followers__username')
    
    # Add filters
    list_filter = ('user',)
    
    # Sorting by user ID or username
    ordering = ('user',)

    # Read-only fields (optional for audit)
    readonly_fields = ('follower_count',)

    # Custom method to calculate the number of followers
    def follower_count(self, obj):
        return obj.followers.count()
    follower_count.short_description = 'Number of Followers'

    # Optional customization for the detail view
    fieldsets = (
        ('User Details', {
            'fields': ('user',),
        }),
        ('Followers Management', {
            'fields': ('followers',),
        }),
    )

# Register the Follower model with the custom FollowerAdmin
admin.site.register(Follower, FollowerAdmin)  """

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Case, When
from .models import Follower, Comment, Post, User

def quick_sort_followers(followers):
    if len(followers) <= 1:
        return followers
    else:
        pivot = followers[0]
        less_than_pivot = [follower for follower in followers[1:] if follower.followers.count() >= pivot.followers.count()]
        greater_than_pivot = [follower for follower in followers[1:] if follower.followers.count() < pivot.followers.count()]
        return quick_sort_followers(less_than_pivot) + [pivot] + quick_sort_followers(greater_than_pivot)

class FollowerAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'user', 'profile_picture','follower_profile_picture', 'follower_count', 'following_count')
    
    # Add search functionality
    search_fields = ('user__username', 'followers__username')
    
    # Add filters
    list_filter = ('user',)
    
    # Sorting by user ID or username
    ordering = ('user',)

    # Read-only fields (optional for audit)
    readonly_fields = ('follower_count',)

    # Custom method to calculate the number of followers
    def follower_count(self, obj):
        return obj.followers.count()
    follower_count.short_description = 'Number of Followers'

    # Custom method to calculate the number of users the current user is following
    def following_count(self, obj):
        return obj.user.following.count()
    following_count.short_description = 'Number of Following'

    # Custom method to display the user's profile picture
    def profile_picture(self, obj):
        if obj.user.profile_pic:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.user.profile_pic.url)
        return "No Image"
    profile_picture.short_description = 'Profile Picture'

    # Custom method to display the follower's profile picture
    def follower_profile_picture(self, obj):
        followers = obj.followers.all()
        if followers:
            return format_html(''.join([f'<img src="{follower.profile_pic.url}" style="max-height: 50px; margin-right: 5px;"/>' for follower in followers if follower.profile_pic]))
        return "No Image"
    follower_profile_picture.short_description = 'Follower Profile Pictures'

    # Override get_queryset to use quick sort
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        followers = list(queryset)
        sorted_followers = quick_sort_followers(followers)
        
        # Create a list of IDs in the sorted order
        sorted_ids = [follower.id for follower in sorted_followers]
        
        # Use Case/When to preserve the order in the queryset
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])
        return queryset.filter(pk__in=sorted_ids).order_by(preserved_order)

admin.site.register(Follower, FollowerAdmin)












# Register your models here.


#admin.site.register(Comment)
#admin.site.register(Follower)
#admin.site.register(Like)
#admin.site.register(Saved)