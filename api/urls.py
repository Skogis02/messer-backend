from django.urls import path
from .views import Register, Login, Logout, VerifySession, GetFriends

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),
    path('verify-session/', VerifySession.as_view()),
    path('get-friends', GetFriends.as_view())
]