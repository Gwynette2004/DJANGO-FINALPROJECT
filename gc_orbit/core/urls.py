from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('create-organization/', views.CreateOrganizationView.as_view(), name='create-organization'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('create-department/', views.CreateDepartmentView.as_view(), name='create-department'),
    path('upload-document/', views.UploadDocumentView.as_view(), name='upload-document'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
