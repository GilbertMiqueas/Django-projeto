from django.contrib.auth.models import User
from django import forms
from django.db.models import Avg, Q
from estoque.models import Livro, Editora, Autor

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ['username', 'email', 'password']

#clase  para mudar o save() do livro
#Cria im FormList
class LivroForm(forms.ModelForm):

    def get_avaliacao_avg(self):
        livros = Livro.objects.filter(
            autores__in=self.cleaned_data['autores']
        ).distinct()
        media = livros.aggregate(Avg('avaliacao'))
        return media.get('avaliacao__avg', 0) or 0

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.avaliacao = self.get_avaliacao_avg()
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Livro
        fields = [
            'nome',
            'paginas',
            'preco',
            'autores',
            'editora',
            'data_de_publcacao',
        ]

class AutorSearchForm(forms.Form):
    nome = forms.CharField(required=False)

    def get_queryset(self):
        q = Q()
        if self.is_valid():
            if self.cleaned_data.get('nome'):
                q = q & Q(nome__icontains=self.cleaned_data['nome'])
            if self.cleaned_data.get('idade'):
                q = q & Q(idade__icontains=self.cleaned_data['idade'])
        return Autor.objects.filter(q)


class LivroSearchForm(forms.Form):
    nome = forms.CharField(required=False)
    autores = forms.CharField(required=False)
    editora = forms.ModelChoiceField(required=False, queryset=Editora.objects)

    def get_queryset(self):
        q = Q()
        if self.is_valid():
            if self.cleaned_data.get('nome'):
                q = q & Q(nome__icontains=self.cleaned_data['nome'])
            if self.cleaned_data.get('autores'):
                q = q & Q(autores__nome__icontains=self.cleaned_data['autores'])
            if self.cleaned_data.get('editora'):
                q = q & Q(editora=self.cleaned_data['editora'])
        return Livro.objects.filter(q)