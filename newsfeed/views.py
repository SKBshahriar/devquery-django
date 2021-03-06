from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from post.models import Post, Tag, Vote, Comment, Saved
from profilesection.models import Follow
from django.contrib.auth.models import User
from profilesection.models import Interest
from django.db.models import Q, Count
from datetime import datetime
from account.choices import tags


class MainView(TemplateView):
    template_name = 'newsfeed/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            following = Follow.objects.filter(follower=request.user)
            interest = Interest.objects.filter(user=request.user)
            posts = Post.objects.filter(
                Q(user__following_user__in=following) |
                Q(tag__name__in=interest.values('tag')) |
                Q(user=request.user)
            ).distinct().order_by('-time')

            pVotes, nVotes, tags, comments, voted, saved = [], [], [], [], [], []

            for post in posts:
                pVotes.append(Vote.objects.filter(post=post).filter(vote_direction='plus').
                              aggregate(num=Count('id'))['num'])
                nVotes.append(Vote.objects.filter(post=post).filter(vote_direction='minus').
                              aggregate(num=Count('id'))['num'])
                comments.append(Comment.objects.filter(post=post).aggregate(num=Count('id'))['num'])
                tags.append(Tag.objects.filter(post=post))
                try:
                    voted.append(Vote.objects.get(post=post, user=request.user))
                except Vote.DoesNotExist:
                    voted.append(None)
                try:
                    saved.append(Saved.objects.get(post=post, user=request.user))
                except Saved.DoesNotExist:
                    saved.append(None)

            context = {
                'posts': zip(posts, pVotes, nVotes, comments, tags, voted, saved),
            }
            return render(request, self.template_name, context)
        return redirect('login')


class CreatePostView(TemplateView):
    template_name = 'newsfeed/create-post.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request,self.template_name)

    def post(self, request):
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES.get('image', False)
        tag = request.POST['tag']
        if image:
            post = Post.objects.create(title=title, description=description, image=image,
                                       time=datetime.now(), user=request.user)
            post.save()
        else:
            post = Post.objects.create(title=title, description=description, time=datetime.now(), user=request.user)
            post.save()
        tag = tag.split(",")
        for t in tag:
            Tag.objects.create(name=t, post=post)
        return redirect('index')


class SearchView(TemplateView):
    template_name = 'newsfeed/search.html'

    def get(self, request, *args, **kwargs):
        key = request.GET['key']
        key_components = key.split(" ")
        users = []
        cnt = 0
        for component in key_components:
            print(component)
            if cnt == 0:
                if component != "":
                    users = User.objects.filter(
                        Q(first_name__icontains=component) |
                        Q(last_name__icontains=component) |
                        Q(username__icontains=component)).filter(is_superuser=False).distinct()
            else:
                if component != "":
                    users = users | User.objects.filter(
                        Q(first_name__icontains=component) |
                        Q(last_name__icontains=component) |
                        Q(username__icontains=component)).filter(is_superuser=False).distinct()
            cnt = cnt + 1

        users = users.distinct()

        posts = Post.objects.filter(
            Q(title__icontains=key) |
            Q(description__icontains=key)
        ).distinct()
        context = {
            "users": users,
            "posts": posts
        }
        return render(request, self.template_name, context)


class SavedView(TemplateView):
    template_name = 'newsfeed/saved.html'

    def get(self, request, *args, **kwargs):
        saved = Saved.objects.filter(user=request.user)
        posts = []
        for sv in saved:
            posts.append(Post.objects.get(pk=sv.post.id))
        context = {
            "posts": posts
        }
        return render(request, self.template_name, context)

