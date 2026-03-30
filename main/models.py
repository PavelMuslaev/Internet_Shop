from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True) # Для реализации читабельных URL


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True) # blank=True - Разрешает быть пустым в админке django
    # Общий пусть будет: /media/products/main, так как media мы настроили в settings
    main_image = models.ImageField(upload_to='products/main/')

    """
    auto_now_add и auto_now — это параметры полей DateTimeField (и DateField) в Django,
    которые автоматически управляют временем.
    
    auto_now_add=True
    Устанавливает текущую дату и время только один раз — в момент создания объекта.
    После этого значение не меняется при последующих сохранениях.
    Обычно используется для поля, хранящего дату создания (created_at).
    
    auto_now=True
    Обновляет поле до текущей даты и времени при каждом сохранении объекта
    (как при создании, так и при изменении). Чаще всего применяется для поля,
    хранящего дату последнего обновления (updated_at).
    
    Таким образом, auto_now_add фиксирует момент создания,
    а auto_now — момент последнего изменения записи.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    # related_name - то как мы видим это в админке.
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product_size')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    # Доступное количество
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.size.name} ({self.stock=}) for {self.product.name}."


class ProductImage(models.Model):
    """
    У нас есть Product.main_image это главна картинка, которую видит пользователь перед тем,
    как открыть товар, класс ProductImage же это внутренни картинки товара, которые видит
    пользователь, когда открыл товар. Так мы разделим логику этих картинок и их
    удобнее будет заполнять.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product_image')
    # extra -  дополнительный
    image = models.ImageField(upload_to='products/extra/')
