from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.contrib.auth.models import User



ADDRESS_CHOICES= (
    ('B','Billing'),
    ('S','Shipping'),

)
class Categories(models.Model):
    title=models.CharField(max_length=20)
    def __str__(self):
        return self.title

class Lables(models.Model):
    title=models.CharField(max_length=20)
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic=models.ImageField(upload_to='profile_pic', default='default.png')
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title= models.CharField(max_length=100)
    price=models.FloatField()
    discount_price=models.FloatField(null=True,blank=True)
    category=models.ManyToManyField(Categories)
    lable=models.ManyToManyField(Lables)
    slug=models.SlugField()
    description=models.TextField()
    image=models.ImageField(upload_to='Images')


    def __str__(self):
        return self.title
    def get_absolute_urls(self):
        return reverse("app1:products",kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("app1:add_to_cart",kwargs={
            'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("app1:remove_from_cart",kwargs={
            'slug':self.slug
        })
    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')


class OrderItem(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    item =models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    ordered= models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    def get_quantity(self):
        return self.quantity

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()



class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    charge_code=models.CharField(max_length=20,blank=True,null=True)
    ref_code=models.CharField(max_length=20,blank=True,null=True)
    items = models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField()
    ordered= models.BooleanField(default=False)
    shipping_address= models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,blank=True,null=True)
    billing_address= models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL,blank=True,null=True)
    payment= models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
    coupon=models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)
    being_delivered= models.BooleanField(default=False)
    received= models.BooleanField(default=False)
    refund_requested= models.BooleanField(default=False)
    refund_granted= models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    def get_total(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address=models.CharField(max_length=100)
    apartment_address=models.CharField(max_length=100)
    country = CountryField(multiple=False)
    state=models.CharField(max_length=100)
    zip=models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default=models.BooleanField(default=False)


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id= models.CharField(max_length=100,blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    amount=models.FloatField()
    timestamp= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code=models.CharField(max_length=15)
    amount=models.FloatField()

    def __str__(self):
        return self.code

class Refund(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    reason=models.TextField()
    accepted=models.BooleanField(default=False)
    email=models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=User)