from django.urls import path
from . import views


urlpatterns = [
    path('<int:post_id>', views.PostView.as_view(), name='post'),
]
