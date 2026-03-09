# from django.db import models

# # apps de terceros
# from model_utils.models import TimeStampedModel

# class Home(TimeStampedModel):
#     title = models.CharField('Nombre', max_length=30)
#     description = models.TextField()
#     about_title = models.CharField('Titulo Nosotros', max_length=50)
#     about_text = models.TextField()
#     contact_email = models.EmailField('Email de Contacto', blank=True,null=True)
#     phone = models.CharField('Telefono de Contacto', max_length=20)

#     class Meta:
#         verbose_name='Pagina Principal'
#         verbose_name_plural='Pagina Principal'

#     def __str__(self):
#         return self.title
