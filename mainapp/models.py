from django.db import models

from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

import sys

User = get_user_model()

#************
#1. Category - Категория товаров
#2. Product - Товар
#3. CartProduct - Товары в корзине
#4. Cart - Корзина
#5. Order - Заказ
#6. Customer - Покупатель
#7. Specifications - Спецификации (Характеристики товара)
#************

class MinResolutionErrorException(Exception):
    pass
    
class MaxResolutionErrorException(Exception):
    pass

# Create your models here:
class LatestProductsManager:
    
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
            
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                #ct_model = ct_model.first()
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
            
        return products



class LatestProducts:
    
    objects = LatestProductsManager()



class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
        
        
        
class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True
    
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Изображение товара")
    description = models.TextField(verbose_name="Описание товара", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Цена")
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # image = self.image
        # img = Image.open(image)
        # min_height, min_width = self.MIN_RESOLUTION
        # max_height, max_width = self.MAX_RESOLUTION
        # if img.height < min_height or img.width < min_width:
            # raise MinResolutionErrorException("Разрешение загружаемого изображения меньше минимального!")
        # if img.height > max_height or img.width > max_width:
            # raise MaxResolutionErrorException("Разрешение загружаемого изображения больше максимального!")
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((200, 200), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        print(self.image.name, name)
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)
        
        
        
class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ")
    display_type = models.CharField(max_length=255, verbose_name="Тип дисплея")
    processor_freq = models.CharField(max_length=255, verbose_name="Частота процессора")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    video = models.CharField(max_length=255, verbose_name="Видеокарта")
    time_without_charge = models.CharField(max_length=255, verbose_name="Время работы аккумулятора")
    
    def __str__(self):
        return F"{self.category.name} : {self.title}"
        
        
        
class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ")
    display_type = models.CharField(max_length=255, verbose_name="Тип дисплея")
    resolution = models.CharField(max_length=255, verbose_name="Разрешение экрана")
    accum_volume = models.CharField(max_length=255, verbose_name="Объём батареи")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    sd = models.BooleanField(default=True)
    sd_volume_max = models.CharField(max_length=255, verbose_name="Максимальный объём встраиваемой памяти")
    main_cam_mp = models.CharField(max_length=255, verbose_name="Главная камера")
    frontal_cam_mp = models.CharField(max_length=255, verbose_name="Фронтальная камера")
    
    def __str__(self):
        return F"{self.category.name} : {self.title}"
        
        
        
class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name="Корзина", on_delete=models.CASCADE, related_name='related_products')
    #product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")
    
    def __str__(self):
        return F"Продукт: {self.product.title} (для корзины)"
        
        
        
class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name="Владелец", on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")
    
    def __str__(self):
        return str(self.id)
        
        
        
class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    
    def __str__(self):
        return F"Покупатель: {self.user.first_name} {self.user.last_name}"
        
        
        
# class Specifications(models.Model):
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # name = models.CharField(max_length=255, verbose_name="Имя товара для характеристик")
    
    # def __str__(self):
        # return F"Характеристики для товара: {self.name}"