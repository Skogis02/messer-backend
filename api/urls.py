from django.urls import path
from .views import Register, Login, VerifySession

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('verify-session', VerifySession.as_view())
]