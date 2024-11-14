from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter todos by the authenticated user"""
        return Todo.objects.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        """Automatically set the `user` field based on the authenticated user"""
        serializer.save(user=self.request.user)
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set `updated_by` to the authenticated user on every update"""
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Perform a soft delete by setting `is_deleted` to True"""
        todo = self.get_object()
        todo.is_deleted = True
        todo.save()
        return Response(
            {"status": "Task marked as deleted"}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated]
    )
    def mark_done(self, request, pk=None):
        try:
            todo = self.get_queryset().get(pk=pk)
            todo.completed = True
            todo.save()

            return Response(
                {"status": "Task marked as done"}, status=status.HTTP_200_OK
            )
        except Todo.DoesNotExist:
            return Response(
                {"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND
            )
