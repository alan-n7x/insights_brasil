from django.urls import path

from .views import estados


urlpatterns = [

    path(
        "estados/",
        estados,
        name="estados"
    ),

]