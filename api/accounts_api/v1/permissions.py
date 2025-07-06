from rest_framework import permissions


class IsAdminOrIsOwner(permissions.BasePermission):
    """
        Admin bo'lsa CRUD amallarga ruxsat, Oddiy foydlanuvchi bo'lsa faqat o'zining obyektiga ruxsat
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user

