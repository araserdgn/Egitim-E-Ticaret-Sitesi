from django.shortcuts import redirect, render

#!
from .models import *
from django.db.models import Q  # AND OR kullanmamızı saglar.
from django.contrib import messages

import iyzipay
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import pprint
from django.core.cache import cache

# ? İYZİCO İÇİN KOD KISMI------------------------------

# ! Canlıya alınınca hepsinin basındaki SENDBOX- kısmını sil
api_key = 'sandbox-3RpYwGyhllvA6vi6lRJjq36fqMltCc5C'
# ! Canlıya alınınca hepsinin basındaki SENDBOX- kısmını sil
secret_key = 'sandbox-U5abrAWwtCOhS5mLNVfH4zTIHORrgogw'
# ! Canlıya alınınca hepsinin basındaki SENDBOX- kısmını sil
base_url = 'sandbox-api.iyzipay.com'



options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


def payment(request):
    context = dict()
    kullanici = request.user
    odeme = Odeme.objects.get(user=kullanici,odendiMi=False)
    price=odeme.total
    buyer = {
        'id': 'BY789',
        'name': kullanici.username,
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': str(kullanici.last_login),
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.5'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.5'
        }
    ]

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1.5',
        'paidPrice': float(price),
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }
    
    # obj={
    #     "isim":"ahmet",
    #     "soyad":"pancar"
    # }
    # print(obj["isim"])

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)
    
    # print(checkout_form_initialize.read().decode('utf-8'))
    
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(json_content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    print(json_content["token"])
    token=json_content['token']
    cache.set('token',token)
    print("************************")
    sozlukToken.append(json_content["token"])
    return HttpResponse(f'<div id="iyzipay-checkout-form" class="responsive">{json_content["checkoutFormContent"]}</div>')


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')
    token =cache.get('token')
    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': token
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    # print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    # print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)


def success(request):
    odeme = Odeme.objects.get(ekleyen=request.user,odendiMi=False)
    odeme.odendiMi=True
    odeme.save()
    basket=Basket.objects.filter(user=request.user,odendiMi=False)
    for baskt in basket:
        baskt.odendiMi=True
        baskt.save()
    messages.success(request,'Ödemeniz Başarılı şekilde olusturuldu')    
    return redirect('index')


def fail(request):
    messages.error(request,'Ödemenizde Bir sorun olustu, Sepete yönleniyorsunuz')
    return redirect('basket')

# ? İYZİCO İÇİN KOD KISMI SONUUUU ---------------------------------------------------------

# Create your views here.
def index(request):
    products=Products.objects.all()
    category = Category.objects.all()
    search=''
    if request.GET.get('search'):
        search = request.GET.get('search')
        products = Products.objects.filter( Q(name__icontains = search) | Q(category__name__icontains=search)) # icontains => arama kısmında yarısını da yazsan onu bulma saglar

    if request.method=='POST':
        if request.user.is_authenticated:
            urunId = request.POST ['urunId']    
            adet = request.POST ['adet']
            myProduct = Products.objects.get(id = urunId)
            if Basket.objects.filter(ekleyen = request.user, product = myProduct, odendiMi = False).exists():
                basket = Basket.objects.get(ekleyen = request.user, product = myProduct, odendiMi = False)
                basket.adet += int(adet)
                # basket.total = myProduct.price * basket.adet 
                basket.save()
            else:
                basket = Basket.objects.create(
                    ekleyen = request.user,
                    product = myProduct,
                    adet = adet,
                    total = myProduct.price * int(adet)
                )
                basket.save()
            return redirect('index')
        else:
            messages.warning(request, 'Girişli Değilsin, Giriş Yap')
            return redirect('login')
    context = {
        'products':products,
        'search':search,
        'category':category
    }
    return render(request,'index.html',context)

def product(request,productId):
    myProduct= Products.objects.get(id=productId)
    context = {
        'product':myProduct
    }
    return render(request, 'detail.html',context)

def kurs(request):
    products=Products.objects.all()
    if request.method=='POST':
        if request.user.is_authenticated:
            urunId = request.POST ['urunId']    
            adet = request.POST ['adet']
            myProduct = Products.objects.get(id = urunId)
            if Basket.objects.filter(ekleyen = request.user, product = myProduct, odendiMi = False).exists():
                basket = Basket.objects.get(ekleyen = request.user, product = myProduct, odendiMi = False)
                basket.adet += int(adet)
                # basket.total = myProduct.price * basket.adet 
                basket.save()
            else:
                basket = Basket.objects.create(
                    ekleyen = request.user,
                    product = myProduct,
                    adet = adet,
                    total = myProduct.price * int(adet)
                )
                basket.save()
            return redirect('kurslar')
        else:
            messages.warning(request, 'Girişli Değilsin, Giriş Yap')
            return redirect('login')
    context = {
        'products':products
    }
    return render(request,'kurslar.html',context)

def baslik(request, mainName):
        category = Category.objects.filter(name=mainName).first()  # Eşleşen kategoriyi al veya None döndür
        if category:
            products = Products.objects.filter(category=category)  # Kategoriye göre ürünleri filtrele
        else:
            products = None  # Eşleşen kategori yoksa products'u None olarak ayarla
            
        context = {
            'malzemeler': products,
            'main':category
        }
        return render(request, 'main.html', context)


def basket(request):
    urunler = Basket.objects.filter(ekleyen = request.user, odendiMi=False)
    toplam =0
    for i in urunler:
        toplam +=i.total
    if request.method=='POST':
        if 'ode' not in request.POST:
            sepetId = request.POST['basketId']
            sepet = Basket.objects.get(id=sepetId)
        if 'sil' in request.POST:
            sepet.delete()
            messages.success(request, 'Ürün Silindi.')
            return redirect('basket')
        elif 'update' in request.POST:
            adet = request.POST['adet']
            if adet == '0':
                sepet.delete()
            else:    
                sepet.adet = adet
                # sepet.total = sepet.product.price * int(adet) 
                sepet.save()
                messages.success(request, 'Sepet başarı ile güncellendi.')
                return redirect('basket')
        elif 'ode' in request.POST:
            if not Odeme.objects.filter(user=request.user,odendiMi=False).exists():
                pass
                odeme = Odeme.objects.create(
                    user = request.user,
                    total = toplam,
                )    
                odeme.urunler.add(*urunler)
                odeme.save()
            return redirect('payment')

    context = {
        'products':urunler,
        'toplam':toplam
    }
    return render(request, 'basket.html',context)


def contact(request):
    return render(request,"contact.html")

