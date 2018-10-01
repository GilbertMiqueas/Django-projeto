#estoque/urls.py
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth.views import LoginView


from . import views

urlpatterns = [
    path('accounts/', include([
        path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
        path('', include('django.contrib.auth.urls')),
        path('cadastro/', views.UserFormView.as_view(), name='cadastro'),
    ])),
    path('autores/', include([
        path('', views.AutorListView.as_view(), name='autor-list'),
        path('taken/', views.autor_nome_registrado, name='autor-taken'),
        path('novo/', views.AutorCreateView.as_view(), name='autor-create'),
        path('<int:pk>/', views.AutorUpdateView.as_view(), name='autor-update'),
    ])),
    path('livros/', include([
        path('', views.LivroSearchFormView.as_view(), name='livro-list'),
        path('jsonlist/', views.LivroJsonListView.as_view(), name='livro-json'),
        path('novo/', views.LivroCreateView.as_view(), name='livro-create'),
        path('<int:pk>/', views.LivroUpdateView.as_view(), name='livro-update'),
    ])),
    path('editoras/', include([
        path('', views.EditoraListView.as_view(), name='editora-list'),
        path('taken/', views.editora_nome_registrado, name='editora-taken'),
        path('novo/', views.EditoraCreateView.as_view(), name='editora-create'),
        path('<int:pk>/', views.EditoraUpdateView.as_view(), name='editora-update'),
    ])),
    path('lojas/', include([
        path('', views.LojaListView.as_view(), name='loja-list'),
        path('taken/', views.loja_nome_registrado, name='loja-taken'),
        path('novo/', views.LojaCreateView.as_view(), name='loja-create'),
        path('<int:pk>/', views.LojaUpdateView.as_view(), name='loja-update'),
    ])),
    path('remover/<int:pk>/<str:app>/<str:model>/', views.GenericDeleteView.as_view(),
     name='generic-delete'),
    path('', views.index, name='index'),   
]