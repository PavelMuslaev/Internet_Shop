from django.contrib import admin
from .models import Category, Size, Product, \
                    ProductImage, ProductSize

# Register your models here.

# Классы инлайн нужны для того, чтобы регистрировать сущности в одном месте.
# Например у нас есть класс Product и класс Size, это две отдельные сущности,
# но заполнять мы бы их хотели в одном едином месте в админ панели.
class ProductImageInline(admin.TabularInline):
    """
    Атрибут extra в классе inline-модели (например, admin.TabularInline) определяет,
    сколько пустых форм для добавления новых связанных объектов будет
    отображаться на странице редактирования родительской модели.

    По умолчанию extra = 3 — показывается три пустые строки для создания новых объектов.

    Если указать extra = 1, будет отображаться только одна пустая форма.

    Это удобно, чтобы ограничить количество одновременно добавляемых объектов или,
    наоборот, увеличить его (например, extra = 5).

    Пустые формы позволяют добавлять новые связанные записи прямо на той же странице,
    не переходя в отдельный интерфейс добавления. После сохранения родительского
    объекта все заполненные формы становятся новыми записями.
    """
    model = ProductImage
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

# Регистрируем класс Product в админ панели
class ProductAdmin(admin.ModelAdmin):
    # Лист, который мы будем видеть при заходе на админку.
    # Там будут описаны все наши продукты.
    # Возьмём только основные параметры
    list_display = ['name', 'category', 'color', 'price']
    list_filter = ['category', 'color', 'name']
    search_fields = ['name', 'color', 'description']
    # Позволяет заполнять параметры, из тех параметров, что у нас уже есть.
    # Например, мы будем вводить name в нашей админке и нас автоматически
    # будет подбираться slug.
    prepopulated_fields = {'slug':('name',)}
    inlines = [ProductSizeInline, ProductImageInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}

class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


# Регестриуем модели и её админ версии
admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Product, ProductAdmin)
