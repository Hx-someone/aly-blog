from django.shortcuts import render

# Create your views here.

def register(request):
    return render(request, 'BDUser/baidu_register.html')
