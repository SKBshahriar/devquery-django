from django.http import JsonResponse
from post.models import Post, Vote, CommentVote, Comment, Reply
from profilesection.models import Follow
from datetime import datetime
from django.contrib.auth.models import User
from post.models import Post, Saved
from django.db.models import Q
from django.contrib import auth


def response(request):
    if request.GET['action'] == 'registration_validation':
        username = request.GET['username']
        email = request.GET['email']
        res = {}
        if User.objects.filter(username=username):
            res['stat'] = "This user name is taken"
        elif User.objects.filter(email=email):
            res['stat'] = "Email already used"
        else:
            res['stat'] = "success"
        return JsonResponse(res)

    if request.GET['action'] == 'login_validation':
        username = request.GET['username']
        password = request.GET['password']
        res = {}
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            res['stat'] = "success"
        else:
            res['stat'] = "Username or password is invalid"
        return JsonResponse(res)

    if request.GET['action'] == 'plus_vote':
        post_id = request.GET['post_id']
        pVote = Vote.objects.filter(user=request.user, post_id=post_id, vote_direction='plus')
        nVote = Vote.objects.filter(user=request.user, post_id=post_id, vote_direction='minus')
        res = {}
        if nVote.exists():
            nVote.delete()
            post = Post.objects.get(pk=post_id)
            Vote.objects.create(user=request.user, post=post, vote_direction='plus')
            res['stat'] = 'swapped'
        elif pVote.exists():
            pVote.delete()
            res['stat'] = 'deleted'
        else:
            post = Post.objects.get(pk=post_id)
            Vote.objects.create(user=request.user, post=post, vote_direction='plus')
            res['stat'] = 'created'
        return JsonResponse(res)

    if request.GET['action'] == 'minus_vote':
        post_id = request.GET['post_id']
        pVote = Vote.objects.filter(user=request.user, post_id=post_id, vote_direction='plus')
        nVote = Vote.objects.filter(user=request.user, post_id=post_id, vote_direction='minus')
        res = {}
        if pVote.exists():
            pVote.delete()
            post = Post.objects.get(pk=post_id)
            Vote.objects.create(user=request.user, post=post, vote_direction='minus')
            res['stat'] = 'swapped'
        elif nVote.exists():
            nVote.delete()
            res['stat'] = 'deleted'
        else:
            post = Post.objects.get(pk=post_id)
            Vote.objects.create(user=request.user, post=post, vote_direction='minus')
            res['stat'] = 'created'
        return JsonResponse(res)

    if request.GET['action'] == 'comment_plus_vote':
        comment_id = request.GET['comment_id']
        pVote = CommentVote.objects.filter(user=request.user, comment_id=comment_id, vote_direction='plus')
        nVote = CommentVote.objects.filter(user=request.user, comment_id=comment_id, vote_direction='minus')
        res = {}
        if nVote.exists():
            nVote.delete()
            comment = Comment.objects.get(pk=comment_id)
            CommentVote.objects.create(user=request.user, comment=comment, vote_direction='plus')
            res['stat'] = 'swapped'
        elif pVote.exists():
            pVote.delete()
            res['stat'] = 'deleted'
        else:
            comment = Comment.objects.get(pk=comment_id)
            CommentVote.objects.create(user=request.user, comment=comment, vote_direction='plus')
            res['stat'] = 'created'
        return JsonResponse(res)

    if request.GET['action'] == 'comment_minus_vote':
        comment_id = request.GET['comment_id']
        pVote = CommentVote.objects.filter(user=request.user, comment_id=comment_id, vote_direction='plus')
        nVote = CommentVote.objects.filter(user=request.user, comment_id=comment_id, vote_direction='minus')
        res = {}
        if pVote.exists():
            pVote.delete()
            comment = Comment.objects.get(pk=comment_id)
            CommentVote.objects.create(user=request.user, comment=comment, vote_direction='minus')
            res['stat'] = 'swapped'
        elif nVote.exists():
            nVote.delete()
            res['stat'] = 'deleted'
        else:
            comment = Comment.objects.get(pk=comment_id)
            CommentVote.objects.create(user=request.user, comment=comment, vote_direction='minus')
            res['stat'] = 'created'
        return JsonResponse(res)

    if request.GET['action'] == 'make_comment':
        comment = request.GET['comment']
        post_id = request.GET['post_id']
        post = Post.objects.get(pk=post_id)
        cmt = Comment.objects.create(comment=comment, time=datetime.now(), post=post, user=request.user)
        cmt.save()
        user_image = request.user.userinfo.image
        if user_image:
            user_image = request.user.userinfo.image.url
        else:
            user_image = "/static/img/user.png"

        res = {
            'user_image': user_image,
            'user_name': request.user.first_name + " " + request.user.last_name,
            'comment': comment,
            'cmt_id': cmt.id,
        }
        return JsonResponse(res)

    if request.GET['action'] == 'search_suggestion':
        text = request.GET['text']
        data = []
        users = User.objects.filter(
            Q(first_name__icontains=text) |
            Q(last_name__icontains=text) |
            Q(username__icontains=text)).distinct()
        for user in users:
            data.append(user.first_name + " " + user.last_name)
        posts = Post.objects.filter(
            Q(title__icontains=text) |
            Q(description__icontains=text)
        ).distinct()
        for post in posts:
            data.append(post.title[:40])
        return JsonResponse(data, safe=False)

    if request.GET['action'] == 'save_post':
        post_id = request.GET['post_id']
        post = Post.objects.get(pk=post_id)
        saved = Saved.objects.filter(post=post, user=request.user)
        res = {}
        if saved.exists():
            saved.delete()
            res['stat'] = "deleted"
        else:
            Saved.objects.create(post=post, user=request.user)
            res['stat'] = "created"
        return JsonResponse(res)

    if request.GET['action'] == 'make_reply':
        comment_id = request.GET['comment_id']
        comment = Comment.objects.get(pk=comment_id)
        reply = request.GET['reply']
        Reply.objects.create(comment=comment, reply=reply, time=datetime.now(), user=request.user)
        user_image = request.user.userinfo.image
        if user_image:
            user_image = request.user.userinfo.image.url
        else:
            user_image = "/static/img/user.png"
        res = {
            'user_image': user_image,
            'user_name': request.user.first_name + " " + request.user.last_name,
            'rep': reply,
        }
        return JsonResponse(res)

    if request.GET['action'] == 'follow':
        user_id = request.GET['user_id']
        user = User.objects.get(pk=user_id)
        res = {}
        follow = Follow.objects.filter(following=user, follower=request.user)
        if follow.exists():
            follow.delete()
            res['stat'] = 'unfollowed'
        else:
            Follow.objects.create(following=user, follower=request.user)
            res['stat'] = 'followed'
        return JsonResponse(res)





