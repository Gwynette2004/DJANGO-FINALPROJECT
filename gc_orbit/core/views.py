import jwt
from datetime import datetime, timedelta
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .models import User, Organization, Department, Document
from .serializers import UserSerializer, OrganizationSerializer, DepartmentSerializer
from .permissions import IsAdmin
from django.conf import settings
import bcrypt
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


# JWT SECRET KEY (you should use a secret key from settings)
JWT_SECRET_KEY = settings.SECRET_KEY

# CREATE ORGANIZATION
class CreateOrganizationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        department_id = data.get('departmentId')

        if not name or not email or not password or not department_id:
            return Response({"error": "Organization name, email, password, and department are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the organization as a User object
        user = User.objects.create_user(
            username=name,
            email=email,
            password=password,
            role='organization',
            department=department
        )

        return Response({"message": "Organization created successfully!", "organizationId": user.id}, status=status.HTTP_201_CREATED)
    
# REGISTER USER
class RegisterUserView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        department_id = data.get('department')
        organization_id = data.get('organizationId')

        if not name or not email or not password or not role:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if role in ['organization', 'dean', 'adviser'] and not department_id:
            return Response({"error": f"{role}s must have a department"}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'admin' and department_id:
            return Response({"error": "Admins should not have a department"}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'adviser' and not organization_id:
            return Response({"error": "Advisers must be assigned to an organization"}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing user with the same email
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=name,
            email=email,
            password=password,
            role=role,
            department_id=department_id,
            organization_id=organization_id
        )

        return Response({"message": f"{role} registered successfully!", "userId": user.id})


# LOGIN (Generate JWT token for all users)
@api_view(['POST'])
@permission_classes([AllowAny])  # Make sure login does NOT require auth
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


# GET USER PROFILE
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "role": user.role,
            "department": user.department.name if user.department else None,
            "organizationId": user.organization.id if user.organization else None
        }
        return Response(user_data)


# CREATE DEPARTMENT
class CreateDepartmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({"error": "Department name is required"}, status=status.HTTP_400_BAD_REQUEST)

        if Department.objects.filter(name=name).exists():
            return Response({"error": "Department already exists"}, status=status.HTTP_400_BAD_REQUEST)

        department = Department.objects.create(name=name)
        return Response({"message": "Department created successfully!", "departmentId": department.id})

class UploadDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        title = data.get('title')
        file = request.FILES.get('file')
        adviser_id = data.get('adviser_id')
        department_id = data.get('department_id')

        if not title or not file or not adviser_id or not department_id:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            adviser = User.objects.get(id=adviser_id, role='adviser')
        except User.DoesNotExist:
            return Response({"error": "Adviser not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.create(
            title=title,
            file=file,
            uploaded_by=request.user,
            adviser=adviser,
            department=department
        )

        # Notify the adviser, dean, and admin (logic can be added here)
        # Example: Send an email or create a notification entry in the database

        return Response({"message": "Document uploaded successfully!", "documentId": document.id}, status=status.HTTP_201_CREATED)