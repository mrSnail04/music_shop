from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.conf import settings
from django.utils.safestring import mark_safe
from utils import upload_function
from django.urls import reverse


class MediaType(models.Model):
    # Тип носителя

    name = models.CharField(max_length=100, verbose_name='Название медианоителя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медианоситель'
        verbose_name_plural = 'Медианосители'


class Member(models.Model):
    # Исполнитель

    name = models.CharField(max_length=100, verbose_name='Имя')
    slug = models.SlugField()
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = 'Музыканты'


class Genre(models.Model):
    # Жанр

    name = models.CharField(max_length=50, verbose_name='Музыкальный жанр')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Artist(models.Model):
    # Исполнитель

    name = models.CharField(max_length=100, verbose_name='Исполнитель/группа')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, verbose_name='Участник', related_name='artist')
    slug = models.SlugField()
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.genre.name}"

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'artist_slug': self.slug})

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class Album(models.Model):
    # Альбом

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Исполнитель')
    name = models.CharField(max_length=250, verbose_name='Название')
    media_type = models.ForeignKey(MediaType, verbose_name='Носитель', on_delete=models.CASCADE)
    songs_list = models.TextField(verbose_name='Трэк-лист')
    release_date = models.DateField(verbose_name='Дата релиза')
    slug = models.SlugField()
    description = models.TextField(verbose_name='Описание', default='Описание появится позже')
    stock = models.IntegerField(verbose_name='Наличие на складе', default=1)
    price = models.DecimalField(verbose_name='Цена', max_digits=9, decimal_places=2)
    offer_of_the_week = models.BooleanField(verbose_name='Предложение недели', default=False)
    image = models.ImageField(upload_to=upload_function)

    def __str__(self):
        return f"{self.id} | {self.artist.name} | {self.name}"

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'artist_slug': self.artist.slug, 'album_slug': self.slug})

    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'


class CartProduct(models.Model):
    # Продук корзины

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(verbose_name='Общая цена', max_digits=9, decimal_places=2)

    def __str__(self):
        return f"Продукт {self.content_object} для корзины"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart (models.Model):
    # Корзина

    owner = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(
        CartProduct, blank=True, verbose_name='Продукты для корзины', related_name='related_cart'
    )
    total_product = models.IntegerField(verbose_name='Общие кол-во товара', default=0)
    final_price = models.DecimalField(verbose_name='Общая цена', max_digits=9, decimal_places=2, null=True, blank=True)
    in_order = models.BooleanField(default=False)
    for_anonymous_owner = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    # Заказ

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ  получен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создание заказа', auto_now=True)
    order_date = models.DateField(verbose_name='Дата получение заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):
    # Покупатель

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    customer_orders = models.ManyToManyField(
        Order, blank=True, verbose_name='Заказы покупателя', related_name='related_customer'
    )

    wishlist = models.ManyToManyField(Album, verbose_name='Список ожидпемого', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Notification(models.Model):
    # Уведомление

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Уведомление для {self.recipient.user.username} | id={self.id}'

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class ImageGallery(models.Model):
    # Галерея изображений

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=upload_function)
    use_in_slider = models.BooleanField(default=False)

    def __str__(self):
        return f"Изображение для {self.content_object}"

    def image_url(self):
        return mark_safe(f'<img src="{self.image.url}" width="auto" height="200px"')

    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = verbose_name
