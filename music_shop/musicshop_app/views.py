from django.shortcuts import render
from django import views
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .models import Artist, Album, Customer, Order, Cart, Genre, CartProduct
from .forms import LoginForm, RegistrationForm


class BaseView(views.View):

    def get(self, request, *args, **kwargs):

        genres = Genre.objects.all()
        albums = Album.objects.all()
        artists = Artist.objects.all()

        context = {
            'genres': genres,
            'albums': albums,
            'artists': artists,
        }
        return render(request, 'base.html', context)


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


class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'login.html', context)


class RegistrationView(views.View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
            )

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)


class ProfileView(views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
        cart = Cart.objects.filter(owner=customer, in_order=False).first()

        return render(
            request,
            'profile.html',
            {'orders': orders, 'cart': cart, 'customer': customer}
        )


class AddToCartView(views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        album_slug = kwargs.get('slug')
        cart = Cart.objects.get(owner=customer, in_order=False)
        content_type = ContentType.objects.get(model='album')
        product = content_type.model_class().objects.get(slug=album_slug)
        cart_product,  created = CartProduct.objects.get_or_create(
            user=cart.owner, cart=cart, content_type=content_type, object_id = product.id, final_price=product.price
        )

        cart.products.add(cart_product)

        # recalc_cart(cart)
        # messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
        return HttpResponseRedirect('/profile/')
