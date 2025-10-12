from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import PlannerTask
from .serializers import PlannerTaskSerializer


class PlannerTaskListCreateView(generics.ListCreateAPIView):
    """
    API view to list all tasks for the authenticated user and create new tasks.

    GET /api/tasks/ (Lists user's tasks)
    POST /api/tasks/ (Creates a new task)
    """
    serializer_class = PlannerTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure users can only see their own tasks.
        """
        # Filter queryset to only include tasks owned by the current authenticated user
        return PlannerTask.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the task's user field to the currently authenticated user upon creation.
        """
        serializer.save(user=self.request.user)


class PlannerTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single task.

    GET /api/tasks/{id}/ (Retrieve)
    PUT/PATCH /api/tasks/{id}/ (Update)
    DELETE /api/tasks/{id}/ (Delete)
    """
    serializer_class = PlannerTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure users can only modify their own tasks.
        """
        # Filter queryset to only include tasks owned by the current authenticated user
        return PlannerTask.objects.filter(user=self.request.user)
