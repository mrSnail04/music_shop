from django.shortcuts import render
from django import views
from .models import Artist, Album


class BaseView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'base.html', {})


class ArtistDetailView(views.generic.DeleteView):

    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'


class AlbumDetailView(views.generic.DeleteView):

    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'
