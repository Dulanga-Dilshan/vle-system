from django.urls import path
from university import views as university_views


app_name= 'university'


urlpatterns = [
    path("materials/<int:id>/download/", university_views.download_material, name='material_download'),
    path("materials/<int:id>/view/", university_views.view_material, name="view_material"),
    path("materials/<int:id>/video/stream/", university_views.stream_material_video, name="material_video_stream"),
]