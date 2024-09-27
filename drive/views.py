from django.shortcuts import render
from .models import User,  Entity
from .serializers import UserSerializer,  EntitySerializer
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
from rest_framework import status,generics
import hashlib
import boto3
from django.shortcuts import get_object_or_404

def generate_hashpath(folder_path, user_id):
    data = f"{folder_path}{user_id}"
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    return hash_value

# Create your views here.
@api_view(['POST'])
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Try to find a user with the provided email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            # Check if the provided password matches the user's password
            if password == user.password:
                # Authentication successful
                # You can perform additional actions after successful login if needed

                # Return the userid in the response (no keytoken anymore)
                response_data = {
                    "message": "Login successful",
                    "userid": user.id
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({"message": "Invalid credentials"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format in the request body"}, status=400)

    # Handle other HTTP methods or errors here
    return JsonResponse({"message": "Method not allowed"}, status=405)

@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        # Get data from the request
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Create a User instance (you should hash the password in a real-world scenario)
        user = User.objects.create(
            name=username,
            password=password,  # Consider hashing the password here
            email=email
        )

        # Generate hashpath for the home folder using folderPath
        home_folder_path = "/"
        hashpath = generate_hashpath(home_folder_path, user.id)

        # Create Entity instance as the home folder
        home_folder = Entity.objects.create(
            folder_path=home_folder_path,
            name=f"{username}'s Home",
            content_type="Folder",
            hashpath=hashpath,  # Assign the generated hashpath
            is_folder=True,
            parent_folder=None,  # Parent folder is null
            user_id=user.id,  # Assign the user ID to the home folder
            url="",  # You can set this as needed
        )
        # print(user)
        if not user:
            return JsonResponse({
            "message": "user already created",
            "email": email
        }, status=status.HTTP_200_CREATED)

        # Return the userid and other user details in the response
        return JsonResponse({
            "user_id": user.id,
            "username": user.name,
            "email": user.email
        }, status=status.HTTP_201_CREATED)
        
    # Handle other HTTP methods or errors here
    return JsonResponse({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET'])
def get_folder_contents(request):
    try:
        # Get user_id and folder_path from the request query parameters
        user_id = request.query_params.get('user_id')
        folder_path = request.query_params.get('folder_path', '/')  # Default to root folder if not specified

        # Calculate the hashpath based on user_id and folder_path
        hashpath = generate_hashpath(folder_path, user_id)

        # Retrieve all entities with the same hashpath
        folder_contents = Entity.objects.filter(user_id=user_id, hashpath=hashpath)

        # Serialize the folder contents
        serialized_contents = []
        for entity in folder_contents:
            serialized_contents.append({
                "entity_id": entity.id,
                "name": entity.name,
                "content_type": entity.content_type,
                "hashpath": entity.hashpath,
                "is_folder": entity.is_folder,
                "user_id": entity.user_id,
                "url": entity.url,
                "folder_path": entity.folder_path,  # Include folder_path in the response
            })

        return Response(serialized_contents, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_entity(request):
    if request.method == 'POST':
        try:
            # Use request.data to parse JSON input
            data = request.data

            # Calculate the hashpath using the folder_path and user.id
            folder_path = data.get('folder_path', '/')  # Default path if not specified
            parent_id = data.get('parent_id')  # Parent entity ID (if creating inside another entity)
            # Generate hashpath using a placeholder for user ID since we removed authentication
            user_id = data.get('user_id')  # Get user ID from the request data
            hashpath = generate_hashpath(folder_path, user_id)  # Generate hashpath

            # Create a new Entity instance based on the 'is_folder' flag
            if data.get('is_folder', True):  # Default to True if 'is_folder' is not provided
                # Create a folder
                new_entity = Entity(
                    folder_path=f"{folder_path}/{data['name']}",
                    name=data['name'],
                    content_type='Folder',
                    hashpath=hashpath,
                    is_folder=True,
                    user_id=user_id,  # Assign user ID from the request data
                    parent_folder_id=parent_id
                )
            else:
                # Ensure URL is provided for files
                if 'url' not in data:
                    return Response({'error': 'Missing required field: url'}, status=status.HTTP_400_BAD_REQUEST)

                # Create a file
                new_entity = Entity(
                    folder_path=f"{folder_path}/{data['name']}",
                    name=data['name'],
                    content_type=data.get('content_type', ''),
                    hashpath=hashpath,
                    is_folder=False,
                    user_id=user_id,  # Assign user ID from the request data
                    url=data['url'],
                    parent_folder_id=parent_id
                )

            new_entity.save()

            # Prepare and return the response
            response_data = {
                "message": "Entity created successfully",
                "entity_id": new_entity.id
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_entity(request):
    if request.method == 'DELETE':
        try:
            # Parse the request body for JSON input
            data = json.loads(request.body.decode('utf-8'))
            entity_id = data.get('entity_id', None)

            if entity_id is not None:
                # Retrieve the Entity by its primary key (entity_id)
                entity = Entity.objects.get(pk=entity_id)

                # Delete the Entity
                entity.delete()

                return Response({'message': 'Entity deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'entity_id not provided in JSON input'}, status=status.HTTP_400_BAD_REQUEST)
        except Entity.DoesNotExist:
            return Response({'error': 'Entity not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def get_entities(request):
    if request.method == 'POST':
        try:
            # The folder path and user_id are extracted from the request data
            folder_path = request.data.get('folder_path', '/')
            user_id = request.data.get('user_id')  # Ensure user_id is provided

            if not user_id or not folder_path:
                return Response({"error": "user_id and folder_path are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate the hashpath using both folder_path and user_id
            hashpath = generate_hashpath(folder_path, user_id)

            # Get all entities with the same hashpath and user_id
            entities = Entity.objects.filter(hashpath=hashpath, user_id=user_id)

            # Serialize the entities and return the data
            serialized_entities = []
            for entity in entities:
                serialized_entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "content_type": entity.content_type,
                    "folder_path": entity.folder_path,  # Include folder_path
                    "is_folder": entity.is_folder,  # Include is_folder flag
                    "user_id": entity.user_id,
                    "url": entity.url,  # Include URL (if relevant)
                })

            return Response(serialized_entities, status=status.HTTP_200_OK)

        except Entity.DoesNotExist:
            return Response({"error": "Entities not found for the specified folder path"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Handle other HTTP methods or errors here
    return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GetPresignedURLView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        filename = request.data.get('filename')

        # Generate a pre-signed URL for the S3 bucket
        s3_client = boto3.client('s3', aws_access_key_id='AKIAWBUEWYQO5KGVHBVY',aws_secret_access_key='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')
        post = s3_client.generate_presigned_post(Bucket='backendc', Key=filename, ExpiresIn=3600)

        return Response({'post': post}, status=status.HTTP_200_OK)
# views.py



@api_view(['PUT'])
def rename_entity(request):
    try:
        data = request.data
        folder_id = data.get('folder_id')
        new_name = data.get('new_name')

        # Retrieve the Entity by folder_id
        entity = get_object_or_404(Entity, pk=folder_id)

        # Update the Entity name
        entity.name = new_name
        entity.save()

        return Response({'message': 'Entity renamed successfully'})
    except Entity.DoesNotExist:
        return Response({'error': 'Entity not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def entity_details(request):
    if request.method == 'POST':
        try:
            # Get the entity ID from the JSON request data
            entity_id = request.data.get('entity_id')

            # Retrieve the entity by its ID
            entity = Entity.objects.get(id=entity_id)

            # Check if the entity is a file
            if entity.is_folder == False:
                # If it's a file, return the URL
                return Response({"url": entity.url}, status=status.HTTP_200_OK)

        except Entity.DoesNotExist:
            return Response({"error": "Entity not found for the specified entity ID"}, status=status.HTTP_404_NOT_FOUND)
        except Entity.MultipleObjectsReturned:
            return Response({"error": "Multiple entities found for the specified entity ID"}, status=status.HTTP_400_BAD_REQUEST)

    # Handle other HTTP methods or errors here
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
