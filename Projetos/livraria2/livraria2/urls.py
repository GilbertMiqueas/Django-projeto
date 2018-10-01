#livraria/urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
	path('', RedirectView.as_view(url='estoque/')),
    path('admin/', admin.site.urls),
    path('estoque/', include('estoque.urls')),
    

]
