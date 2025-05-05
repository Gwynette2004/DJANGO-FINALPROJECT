# GC-Orbit API Documentation

This is the backend API documentation for **GC-Orbit**, a document tracking system for student organizations, built with Django and Django REST Framework.

---
🔐 Authentication

### `POST /api/login/`
Authenticate a user and return JWT tokens.

- **Headers:**  
  `Content-Type: application/json`

- **Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}

{
  "refresh": "JWT_REFRESH_TOKEN",
  "access": "JWT_ACCESS_TOKEN"
}

Create Organization
Method: POST

URL: /api/create-organization/

Headers:

Authorization: Bearer <access-token> (Admin only)

Body:
{
  "name": "Org Name",
  "email": "org@example.com",
  "password": "password123",
  "departmentId": 1
}

{
  "message": "Organization created successfully!",
  "organizationId": 5
}

Register User
Method: POST

URL: /api/register/

Headers:

Authorization: Bearer <access-token> (Admin only)

Body:


{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "pass123",
  "role": "dean",
  "department": 1,
  "organizationId": null
}

{
  "message": "dean registered successfully!",
  "userId": 6
}

Create Department
Method: POST

URL: /api/create-department/

Headers:

Authorization: Bearer <access-token> (Admin only)

Body:

{
  "name": "Computer Science"
}

{
  "message": "Department created successfully!",
  "departmentId": 2
}

Upload Document
Method: POST

URL: /api/upload-document/

Headers:

Authorization: Bearer <access-token>

Content-Type: multipart/form-data

Body (form-data):

title: "Final Report"

file: (Attach a file)

adviser_id: 4

department_id: 2


{
  "message": "Document uploaded successfully!",
  "documentId": 9
}

Roles & Permissions
admin: Can create departments, organizations, users
organization: Can upload documents
dean: Can approve/reject documents (future feature)
adviser: Can comment on documents (future feature)

Notes
All protected routes require an Authorization header with a JWT:

Authorization: Bearer <your-token>
