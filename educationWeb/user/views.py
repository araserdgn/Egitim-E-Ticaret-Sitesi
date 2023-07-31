from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

# Create your views here.

def userRegister(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST) #inputlardan gelen bilgileri REQUEST.POST ile çekiyoruz
        print(request.POST) # POST ile gelen verileri görüyoruz
        if form.is_valid(): # Form hatasız iseee
            form.save()
            messages.success(request, 'Kayıt Basarılıdır, giriş yap.')
            return redirect('login') #kayıt olduktan sonra index sayfaya yönlendik
    context = {
        'form':form
    }
    return render (request, 'register.html',context)

def userLogin(request):
    if request.method=='POST':
        kullanici=request.POST['kullanici']
        sifre=request.POST['sifre']

        user=authenticate(request,username=kullanici,password=sifre)

        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request, 'Kullanıcı adı veya Şifre Hatalıdır.')
            return redirect('login')
    return render(request,'login.html')    

def userLogout(request):
    logout(request)
    return redirect('index')
