	
from django.db import models


class Autor(models.Model):
    nome = models.CharField(max_length=255)
    idade = models.IntegerField()

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"

    def __str__(self):
        return self.nome


class Editora(models.Model):
    nome = models.CharField(max_length=255)
    avaliacao = models.IntegerField()

    class Meta:
        verbose_name = "Editora"
        verbose_name_plural = "Editoras"

    def __str__(self):
        return self.nome


class Livro(models.Model):
    nome = models.CharField(max_length=255)
    paginas = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    avaliacao = models.FloatField()
    autores = models.ManyToManyField(Autor)
    editora = models.ForeignKey(Editora, on_delete=models.CASCADE)
    data_de_publcacao = models.DateField()
    sinopse = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

    def __str__(self):
        return self.nome


class Loja(models.Model):
    nome = models.CharField(max_length=255)
    livros = models.ManyToManyField(Livro)
    quatidade_de_clientes = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"

    def __str__(self):
        return self.nome