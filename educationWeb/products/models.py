from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,verbose_name="Kategori Adı")

    def __str__(self):
        return self.name
    

class SeriNo(models.Model):
    no = models.CharField(max_length=100)

    def __str__(self):
        return self.no
    
class AltKategori(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name    
    
class Products(models.Model):
    category= models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True) #! İstenilen kadar ürün , Category baglanabilir
    seri_no=models.OneToOneField(SeriNo,on_delete=models.CASCADE,null=True,blank=True)
    alt_kategori=models.ManyToManyField(AltKategori,blank=True)
    name=models.CharField(max_length=100,verbose_name="Ürün İsmi:")
    description=RichTextField(max_length=500,verbose_name="Ürün Açıklaması:",null=True)
    price=models.IntegerField(verbose_name="Ürün Fiyatı: ",null=True)
    image=models.ImageField(upload_to='product/',null=True,verbose_name="Ürün Resmi: ")
    
    def __str__(self):
        return self.name
    



    #DATABASE Relationship ( veritabanı ilişkileri) 
    # many to one (foreignkey) (Bir kategori var ona herkes baglanır , ama baska kateg. baglanamaz gbi düşün)
    # manytomany
class Basket(models.Model):
    ekleyen = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    adet=models.IntegerField()
    total=models.IntegerField()
    odendiMi=models.BooleanField(default=False, verbose_name="Tutar Ödendi mi ?") # Checkbox verir bize, ödendiyse tik atılır

    def __str__(self):
        return self.ekleyen.username
    
    def save(self,*args,**kwargs):
        self.total = self.product.price * int(self.adet)
        super(Basket,self).save(*args,**kwargs)
        # SAVE FONK. KAYIT OLUNCA YAPILAN DEĞİŞ. GÖSTERDİK , oto kayıt seklinde olacaklar dusun

class Odeme(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)        
    urunler = models.ManyToManyField(Basket)
    total = models.IntegerField()
    odendiMi = models.BooleanField(default=False)
    tarih=models.DateTimeField(auto_now_add=True) #auto_now_add => O ANKİ SAATİ GÖSTERİR

    def __str__(self):
        return self.user.username