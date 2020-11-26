from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("wiki/create/", views.create, name="create"),
    path("wiki/random/", views.random_page, name="random"),
    path("wiki/edit/", views.edit, name="edit")
]
