from django.urls import path
from . import views
from .views import create_user,get_folder_contents,login_view, delete_entity,create_entity,get_entities,GetPresignedURLView,rename_entity
urlpatterns = [
    path('create_user/', create_user, name='create_user_api'),
    path('create_entity/',create_entity, name='create_entity'),
    path('get_folder_contents/', get_folder_contents, name='get_folder_contents'),
    path('delete_entity/', delete_entity, name='delete_entity'), 
    path('login/', login_view, name='login_view'),
    path('get_entities/', get_entities, name='get_entities'),
    path('get_presigned_url/', GetPresignedURLView.as_view(), name='get_presigned_url'),
    path('rename_entity/', rename_entity, name='rename_entity'),
    path('entity_details/', views.entity_details, name='entity_details'),
      
]
