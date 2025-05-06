import jwt
from datetime import datetime, timedelta
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .models import User, Organization, Department, Document
from .serializers import UserSerializer, OrganizationSerializer, DepartmentSerializer, DocumentSerializer
from .permissions import IsAdmin
from django.conf import settings
import bcrypt
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django_ratelimit.decorators import ratelimit


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


from django_ratelimit.core import is_ratelimited

class UploadDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("Request user:", getattr(request, 'user', None))
        print("Is authenticated:", getattr(request.user, 'is_authenticated', False))
        print("Request META:", request.META.get('REMOTE_ADDR', 'No IP found'))

        # Manually check rate limiting
        ratelimited = is_ratelimited(
            request=request,
            group=None,
            fn=self.post,
            key='user_or_ip',
            rate='5/m',
            method='POST',
            increment=True
        )
        print("Is ratelimited:", ratelimited)

        if ratelimited:
            return Response({"error": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Proceed with the rest of the logic
        data = request.data
        title = data.get('title')
        file = request.FILES.get('file')
        adviser_id = data.get('adviser_id')
        department_id = data.get('department_id')

        # Validate required fields
        if not title or not file or not adviser_id or not department_id:
            return Response({"error": "All fields (title, file, adviser_id, department_id) are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate adviser existence
        try:
            adviser = User.objects.get(id=adviser_id, role='adviser')
        except User.DoesNotExist:
            return Response({"error": f"Adviser with ID {adviser_id} does not exist or is not an adviser"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate department existence
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"error": f"Department with ID {department_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the document
        document = Document.objects.create(
            title=title,
            file=file,
            uploaded_by=request.user,
            adviser=adviser,
            department=department
        )

        return Response({"message": "Document uploaded successfully!", "documentId": document.id}, status=status.HTTP_201_CREATED)

    


class ViewDocumentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print("Request user:", getattr(request, 'user', None))
        print("Is authenticated:", getattr(request.user, 'is_authenticated', False))
        print("Request META:", request.META.get('REMOTE_ADDR', 'No IP found'))

        # Manually check rate limiting
        ratelimited = is_ratelimited(
            request=request,
            group=None,
            fn=self.get,
            key='user_or_ip',
            rate='5/m', 
            method='GET',
            increment=True
        )
        print("Is ratelimited:", ratelimited)

        if ratelimited:
            return Response({"error": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Get the logged-in user's role
        user = request.user
        role = user.role

        # Base queryset for documents
        documents = Document.objects.all()

        # Role-based filtering
        if role == 'adviser':
            # Advisers can only see documents assigned to them
            documents = documents.filter(adviser=user)
        elif role == 'dean':
            # Deans can see all documents in their department
            if user.department:
                documents = documents.filter(department=user.department)
            else:
                return Response({"error": "Dean does not belong to any department"}, status=status.HTTP_400_BAD_REQUEST)
        elif role == 'admin':
            # Admins can see all documents (no filtering needed)
            pass
        elif role == 'organization':
            # Organizations can only see documents they uploaded
            documents = documents.filter(uploaded_by=user)
        else:
            # Other roles cannot view documents
            return Response({"error": "You do not have permission to view documents"}, status=status.HTTP_403_FORBIDDEN)

        # Check if no documents are available
        if not documents.exists():
            print("No documents available for the current user.")  # Console log

        # Serialize the filtered documents
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
