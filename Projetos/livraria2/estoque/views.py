#estoque/views.py
from django.apps import apps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.generic.edit import FormMixin, ModelFormMixin
from django.urls import reverse_lazy
from django import forms
from django.db.models import Avg, Q

from estoque.forms import LivroForm, LivroSearchForm, AutorSearchForm
from estoque.models import Autor, Livro, Editora, Loja
from estoque.forms import UserForm


#request para index
def index(request):
    livro_mais_barato = Livro.objects.order_by('-preco').last()
    livro_mais_caro = Livro.objects.order_by('-preco').first()
    livro_preco_medio = Livro.objects.filter().aggregate(Avg('preco')) or 0
    qtd_autores = Autor.objects.count()
    qtd_editoras = Editora.objects.count()
    qtd_livros = Livro.objects.count()
    qtd_lojas = Loja.objects.count()
    return render(request, 'estoque/index.html', {
        'livro_mais_barato': livro_mais_barato,
        'livro_mais_caro': livro_mais_caro,
        'livro_preco_medio': livro_preco_medio.get('preco__avg', 0),
        'qtd_autores': qtd_autores,
        'qtd_editoras': qtd_editoras,
        'qtd_livros': qtd_livros,
        'qtd_lojas': qtd_lojas,
    })



#request para ver se já existe o autor
def autor_nome_registrado(request):
	nome = request.GET.get('nome', None)
	data = {
		'is_taken': Autor.objects.filter(nome__iexact=nome).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'O autor ja esta cadastrado'
	return JsonResponse(data)

#request para ver se já existe a loja
def loja_nome_registrado(request):
	nome = request.GET.get('nome', None)
	data = {
		'is_taken': Loja.objects.filter(nome__iexact=nome).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'A loja ja esta cadastrado'
	return JsonResponse(data)

#request para cer se já existe a editora
def editora_nome_registrado(request):
	nome = request.GET.get('nome', None)
	data = {
		'is_taken': Editora.objects.filter(nome__iexact=nome).exists()
	}
	if data['is_taken']:
		data['error_message'] = 'A editora ja esta cadastrado'
	return JsonResponse(data)


#clase para cadastrar usuario
class UserFormView(View):
	form_class = UserForm
	template_name = 'estoque/cadastro.html'

	#exibe um formulário em branco
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			#cleaned (normaliza) data
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			#retorna objetos User se credenciais são corretas
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('/estoque/accounts/login')
		return render(request, self.template_name, {'form': form})

#clase generica para apagar objeto especificado
@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class GenericDeleteView(DeleteView):
    model = None
    template_name = 'estoque/confirm_delete.html'

    def get_object(self):
        ModelClass = apps.get_model(
            app_label=self.kwargs['app'],
            model_name=self.kwargs['model']
        )
        obj = get_object_or_404(ModelClass, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return self.request.GET.get('success_url', '/')

#clase para um search com formlist
class SearchFormListView(FormMixin, ListView):
	def get(self, request, *args, **kwargs):
		self.form = self.get_form(self.get_form_class())
		self.object_list = self.form.get_queryset()
		return self.render_to_response(
			self.get_context_data(object_list=self.object_list, form=self.form))

	def get_form_kwargs(self):
		return {'initial': self.get_initial(), 'data': self.request.GET}

#Adicionar automaticamente o nome da pagina com vervose_name
class PageInfoMixin(object):
	page_info = None

	def get_page_info(self):
		if self.model:
			return {
				'page_info': self.model_meta.vervose_name,
				'page_info_plural': self.model_meta.vervose_name_plural,
			}	
		return None

	def get_context_data(self, **kwargs):
		if self.page_info is None:
			kwargs['page_info'] = self.get_page_info()
		return super().get_context_data(**kwargs)

##############################################################################

#clases do Livro
class LivroListView(ListView):
	model = Livro


class LivroSearchFormView(PageInfoMixin, SearchFormListView):
	model = Livro
	form_class = LivroSearchForm

	def get_page_info(self):
		return 'Livros: %s' % (Livro.objects.count())

class JsonListMixin(object):
	json_fields = []

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset().values_list(*self.json_fields)
		json_dict = {
			'header': self.json_fields,
			'object_list': list(self.object_list)
		}
		return JsonResponse(json_dict)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LivroJsonListView(JsonListMixin, LivroListView):
	json_fields = [
		'nome',
		'paginas',
		'preco',
		'avaliacao',
		'editora__nome',
		'autores__nome',
	]

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LivroCreateView(CreateView):
	model = Livro
	form_class = LivroForm
	success_url = reverse_lazy('livro-list')

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LivroUpdateView(UpdateView):
	model = Livro
	fields = '__all__'
	success_url = reverse_lazy('livro-list')


#########################################################################################

#clases do Autor
@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class AutorListView(ModelFormMixin, ListView):
	fields = '__all__'
	model = Autor

	def get(self, request, *args, **kwargs):
		self.object = None
		return super().get(request, *args, **kwargs)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class AutorCreateView(CreateView):
	model = Autor
	fields = '__all__'
	success_url = reverse_lazy('autor-list')

	def form_valid(self, form):
		if self.request.is_ajax():
			obj = form.save()
			return JsonResponse({
				'obj': {'nome': obj.nome, 'idade': obj.idade,}
				})
		return super().form_valid(form)

	def form_invalid(self, form):
		if self.request.is_ajax():
			return JsonResponse({
				'errors': form.errors, 'non_field_errors': form.non_field_errors()
				})
		return super().form_invalid(form)


@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class AutorUpdateView(UpdateView):
	model = Autor
	fields = '__all__'
	success_url = reverse_lazy('autor-list')

#########################################################################################

#clases de Editora
@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class EditoraListView(ModelFormMixin, ListView):
	fields = '__all__'
	model = Editora	

	def get(self, request, *args, **kwargs):
		self.object = None
		return super().get(request, *args, **kwargs)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class EditoraCreateView(CreateView):
	fields = '__all__'
	model = Editora
	success_url = reverse_lazy('editora-list')

	def form_valid(self, form):
		if self.request.is_ajax():
			obj = form.save()
			return JsonResponse({
				'obj': {'nome': obj.nome, 'avaliacao': obj.avaliacao}
				})
		return super().form_valid(form)

	def form_invalid(self, form):
		if self.request.is_ajax():
			return JsonResponse({
				'errors': form.errors, 'non_field_errors': form.non_field_errors()
				})
		return super().form_invalid(form)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class EditoraUpdateView(UpdateView):
	fields = "__all__"
	model = Editora
	success_url = reverse_lazy('editora-list')

########################################################################################

#clases de Loja
@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LojaListView(ModelFormMixin, ListView):
	fields = "__all__"
	model = Loja

	def get(self, request, *args, **kwargs):
		self.object = None
		return super().get(request, *args, **kwargs)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LojaCreateView(CreateView):
	fields = '__all__'
	model = Loja
	success_url = reverse_lazy('loja-list')

	def form_valid(self, form):
		if self.request.is_ajax():
			obj = form.save()
			return JsonResponse({
				'obj': {'nome': obj.nome, 'livros': obj.livros, 'quatidade_de_clientes': obj.quatidade_de_clientes}
				})
		return super().form_valid(form)

	def form_invalid(self, form):
		if self.request.is_ajax():
			return JsonResponse({
				'errors': form.errors, 'non_field_errors': form.non_field_errors()
				})
		return super().form_invalid(form)

@method_decorator(login_required(login_url="/estoque/accounts/login/"), name='dispatch')
class LojaUpdateView(UpdateView):
	fields = '__all__'
	model = Loja
	success_url = reverse_lazy('loja-list')
	