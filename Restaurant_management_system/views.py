from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404


def index(request):
    return render(request, 'index.html')





def table_detail(request, table_number):
    table = get_object_or_404(Table, number=table_number)
    return render(request, 'table_detail.html', {'table': table})
