#from django import forms:
from PIL import Image

#from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.forms import ModelChoiceField, ModelForm

from django.contrib import admin

from django.utils.safestring import mark_safe

from .models import *



class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True, 'style': 'background: lightgray;'
            })
            
    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data



# ПЕРЕОПРЕДЕЛЯЕМ НАЗВАНИЕ ЗАГРУЖЕННОГО ФАЙЛА (ИСКЛЮЧАЕМ ИЗ НЕГО ЛИШНИЕ СИМВОЛЫ, ДОБАВЛЯЕМЫЕ Django):
'''
class NotebookAdminForm(ModelForm):

    # Перенесено в тело класса (модели) 'Product' в models.py:
    # MIN_RESOLUTION = (400, 400)
    # MAX_RESOLUTION = (800, 800)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe(
            """<span style="color:red; font-size:14px;">При загрузке изображения с разрешением больше {}x{} оно будет обрезано!</span>
            """.format(
                *Product.MAX_RESOLUTION
            )
        )
'''        
    # def clean_image(self):
        # image = self.cleaned_data['image']
        # img = Image.open(image)
        # #print(img.width, img.height)
        
        # min_height, min_width = Product.MIN_RESOLUTION
        # max_height, max_width = Product.MAX_RESOLUTION
        # if image.size > Product.MAX_IMAGE_SIZE:
            # raise ValidationError("Размер загружаемого изображения не должен превышать 3Mb!")
        # if img.height < min_height or img.width < min_width:
            # raise ValidationError("Разрешение загружаемого изображения меньше минимального!")
        # if img.height > max_height or img.width > max_width:
            # raise ValidationError("Разрешение загружаемого изображения больше максимального!")
        
        # return image



# ИСКЛЮЧАЕМ ЛИШНИЕ КАТЕГОРИИ В АДМИНКЕ:

# class NotebookCategoryChoiceField(forms.ModelChoiceField):
    # pass
    
    

class NotebookAdmin(admin.ModelAdmin):

    #form = NotebookAdminForm
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        
        
# class SmartphoneCategoryChoiceField(forms.ModelChoiceField):
    # pass
    
    

class SmartphoneAdmin(admin.ModelAdmin):

    change_form_template = 'admin.html'
    form = SmartphoneAdminForm
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        
        
# Register your models here:
admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)