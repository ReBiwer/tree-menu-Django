from django.shortcuts import render

# Create your views here.

def menu_example(request):
    return render(request, 'tree_menu/example.html')
