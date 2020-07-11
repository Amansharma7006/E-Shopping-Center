from django.contrib import admin
from .models import OrderItem,Item,Order,Payment,Coupon,Refund,Address,UserProfile,Categories,Lables
from app1.forms import ProfileUpdateForm
# Register your models here.

def make_refund_accepted(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=True)

make_refund_accepted.short_description='Update order to Refund Granted'

class OrderAdmin(admin.ModelAdmin):
    list_display=['user','ordered','being_delivered','received','refund_requested','refund_granted','shipping_address',
                'billing_address','payment','coupon']
    list_display_links=['user','shipping_address','billing_address','payment','coupon']
    list_filter=['ordered','being_delivered','received','refund_requested','refund_granted']
    search_fields=[
        'user__username',
        'ref_code'
    ]
    actions=[make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display=['user','street_address','apartment_address','country',
        'zip','address_type','default'
    ]
    list_filter=['default','address_type','country']
    search_fields= ['user','street_address','apartment_address','zip']
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Item)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Categories)
admin.site.register(Lables)
admin.site.register(Address,AddressAdmin)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=['user','profile_pic']
admin.site.register(UserProfile,UserProfileAdmin)
# Register your models here.
