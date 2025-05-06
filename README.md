GC-Orbit Backend API
====================

This project contains the core backend APIs for GC-Orbit, a document tracking and user management system designed for student organizations and administrative roles.


Authentication
--------------

Uses JWT tokens (access & refresh) for user authentication. Tokens are returned upon successful login.

Rate Limiting
-------------

Endpoints like `upload-document/` and `view-documents/` are rate-limited to 5 requests per minute per user or IP.

API Endpoints
-------------

1. **Login**
   - `POST /login/`
   - Request:
     ```json
     {
       "email": "user@example.com",
       "password": "yourpassword"
     }
     ```
   - Response:
     ```json
     {
       "refresh": "your-refresh-token",
       "access": "your-access-token"
     }
     ```

2. **Create Organization** (Admin only)
   - `POST /create-organization/`
   - Headers: `Authorization: Bearer <access_token>`
   - Request:
     ```json
     {
       "name": "Org Name",
       "email": "org@example.com",
       "password": "securepassword",
       "departmentId": 1
     }
     ```

3. **Register User** (Admin only)
   - `POST /register/`
   - Headers: `Authorization: Bearer <access_token>`
   - Request:
     ```json
     {
       "name": "John Doe",
       "email": "john@example.com",
       "password": "password123",
       "role": "dean",
       "department": 1,
       "organizationId": 2
     }
     ```

4. **User Profile**
   - `GET /profile/`
   - Headers: `Authorization: Bearer <access_token>`
   - Response:
     ```json
     {
       "id": 1,
       "name": "Admin",
       "email": "admin@example.com",
       "role": "admin",
       "department": null,
       "organizationId": null
     }
     ```

5. **Create Department** (Admin only)
   - `POST /create-department/`
   - Headers: `Authorization: Bearer <access_token>`
   - Request:
     ```json
     {
       "name": "Computer Science"
     }
     ```

6. **Upload Document** (Rate-limited)
   - `POST /upload-document/`
   - Headers: `Authorization: Bearer <access_token>`
   - Form Data:
     ```
     title: Project Plan
     file: <attach file>
     adviser_id: 5
     department_id: 2
     ```

7. **View Documents** (Rate-limited)
   - `GET /view-documents/`
   - Headers: `Authorization: Bearer <access_token>`
   - Returns filtered documents based on user role.

Getting Started
---------------

1. Clone the repository and install dependencies
2. Configure your `.env` and `settings.py` (set `SECRET_KEY`, JWT settings, etc.)
3. Run migrations
4. Start your development server
