from profilesection.models import UserInfo, Interest


def add_variable_to_context(request):
    if request.user.is_authenticated:
        try:
            user_profile_pic = UserInfo.objects.get(user=request.user)
        except UserInfo.DoesNotExist:
            return {'': ''}
        if user_profile_pic:
            user_profile_pic = user_profile_pic.image
        return {
            'user_profile_pic': user_profile_pic,
        }
    return {'': ''}
