from rest_framework import permissions


class IsEmployee(permissions.BasePermission):

    def has_permission(self, request, view):
        return hasattr(request.user, 'employeeprofile')


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'managerprofile')