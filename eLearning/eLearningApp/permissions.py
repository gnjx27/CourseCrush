from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow access only if user is teacher
        return request.user.role == 'teacher'
    
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow access only if user is student
        return request.user.role == 'student'
    