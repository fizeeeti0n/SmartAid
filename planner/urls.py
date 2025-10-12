from django.urls import path
from . import views

# URL Namespace for the planner app
app_name = 'planner'

urlpatterns = [
    # Route for listing all tasks and creating a new task: /api/tasks/
    path('tasks/',
         views.PlannerTaskListCreateView.as_view(),
         name='task-list-create'),

    # Route for retrieving, updating, or deleting a specific task: /api/tasks/1/
    path('tasks/<int:pk>/',
         views.PlannerTaskRetrieveUpdateDestroyView.as_view(),
         name='task-detail'),
]
