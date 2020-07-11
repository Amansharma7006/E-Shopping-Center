from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView,View
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from .forms import SignupForm,CheckoutForm,CouponForm,RefundForm,PaymentForm,UserUpdateForm, ProfileUpdateForm
from .models import Item,OrderItem,Order,Address,Payment,Coupon,Refund,UserProfile
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.


def shirt(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Shirt")
    return render(request,"inner/shirt.html",{'shopping':shopping})
def Jeans(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Jeans")
    return render(request,"inner/jeans.html",{'shopping':shopping})
def Jackets(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Jackets")
    return render(request,"inner/jackets.html",{'shopping':shopping})
def Shoes(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Shoes")
    return render(request,"inner/shoes.html",{'shopping':shopping})

def rental_car(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Rental Car")
    return render(request,"inner/Rental_car.html",{'shopping':shopping})

def own_car(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Own Car")
    return render(request,"inner/Own_car.html",{'shopping':shopping})

def rental_bike(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Rental Bike")
    return render(request,"inner/rental_bike.html",{'shopping':shopping})

def own_bike(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Own Bike")
    return render(request,"inner/own_bike.html",{'shopping':shopping})

def rental_flats(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Rental Flats")
    return render(request,"inner/flats.html",{'shopping':shopping})

def south(request):
    shopping=Item.objects.all().filter(lable__title__icontains="Snacks")
    return render(request,"inner/south.html",{'shopping':shopping})


def shopping(request):
    shopping=Item.objects.all().filter(category__title__icontains="Shopping")
    return render(request,"inner/shop.html",{'shopping':shopping})


def rental(request):
    rental=Item.objects.filter(category__title__icontains="Rental")
    return render(request,"inner/rental.html",{'rental':rental})


def hotel(request):
    shopping=Item.objects.all().filter(category__title__icontains="Hotels")
    return render(request,"inner/hotel.html",{'shopping':shopping})


def food(request):
    shopping=Item.objects.all().filter(category__title__icontains="Food")
    return render(request,"inner/food.html",{'shopping':shopping})



def useradd(request):
    if request.method=='POST':
        u_form= UserUpdateForm(request.POST,instance=request.user)
        p_form= ProfileUpdateForm(request.POST,
                                request.FILES,
                                instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('app1:home')
    else:
        u_form= UserUpdateForm(instance=request.user)
        p_form= ProfileUpdateForm(instance=request.user.userprofile)

    context={
        'u_form':u_form,
        'p_form':p_form,
        }
    return render(request,'userprofile_form.html',context)



# Create your views here.


def listing(request):
    shopping=Item.objects.all().filter(category__title__icontains="Hotels")
    return render(request,"listing.html",{'shopping':shopping})


def category(request):
    shopping=Item.objects.all().filter(category__title__icontains="Hotels")
    return render(request,"category.html",{'shopping':shopping})


def contact(request):
    return render(request,"contact.html")


def about(request):
    return render(request,"about.html")


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid=True
    for field in values:
        if field == '':
            valid=False
    return valid




class CheckoutView(View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            form=CheckoutForm()
            context={
                'form':form,
                'couponform':CouponForm(),
                'order':order,
                'DISPLAY_COUPON_FORM':True
            }

            shipping_address_qs=Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs=Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})
            return render(self.request,'checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(request,"You do not have active Order")
            return redirect("app1:checkout")


    def post(self,*args,**kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():

                use_default_shipping=form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using default shipping address")
                    address_qs=Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address=address_qs[0]
                        order.shipping_address=shipping_address
                        order.save()
                    else:
                        messages.info(self.request,"No Default shipping address Available")
                        return redirect("app1:checkout")
                else:
                    print("user is entering in new shipping Address")

                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_state = form.cleaned_data.get('shipping_state'),
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    #same_shipping_address = form.cleaned_data.get(same_shipping_address)
                    #save_info = form.cleaned_data.get(save_info)
                    if is_valid_form(['shipping_address1','shipping_country','shipping_zip']):
                        shipping_address=Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            state=shipping_state,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address=shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default=True
                            shipping_address.save()
                    else:
                        messages.info(self.request,"Please fill in required shipping address fields")

                    use_default_billing=form.cleaned_data.get('use_default_billing')
                    same_billing_address=form.cleaned_data.get('same_billing_address')
                    if same_billing_address:
                        billing_address=shipping_address
                        billing_address.pk=None
                        billing_address.save()
                        billing_address.address_type='B'
                        billing_address.save()
                        order.billing_address=billing_address
                        order.save()
                    elif use_default_billing:
                        print("Using default billing address")
                        address_qs=Address.objects.filter(
                            user=self.request.user,
                            address_type='B',
                            default=True
                        )
                        if address_qs.exists():
                            billing_address=address_qs[0]
                            order.billing_address=billing_address
                            order.save()
                        else:
                            messages.info(self.request,"No Default billing address Available")
                            return redirect("app1:checkout")
                    else:
                        print("user is entering in new billing Address")

                        billing_address1 = form.cleaned_data.get('billing_address')
                        billing_address2 = form.cleaned_data.get('billing_address2')
                        billing_country = form.cleaned_data.get('billing_country')
                        billing_state = form.cleaned_data.get('billing_state'),
                        billing_zip = form.cleaned_data.get('billing_zip')
                        #same_shipping_address = form.cleaned_data.get(same_shipping_address)
                        #save_info = form.cleaned_data.get(save_info)
                        if is_valid_form(['billing_address1','billing_country','billing_zip']):
                            billing_address=Address(
                                user=self.request.user,
                                street_address=billing_address1,
                                apartment_address=billing_address2,
                                country=billing_country,
                                state=billing_state,
                                zip=billing_zip,
                                address_type='B'
                            )
                            billing_address.save()
                            order.billing_address=billing_address
                            order.save()

                            set_default_billing = form.cleaned_data.get('set_default_billing')
                            if set_default_billing:
                                billing_address.default=True
                                billing_address.save()
                        else:
                            messages.info(self.request,"Please fill in required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')


                if payment_option == 'S':
                    return redirect('app1:payment',payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('app1:payment',payment_option='payPal')
                else:
                    messages.warning(self.request,"Invalid Option selected")
                    return redirect('app1:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("app1:order_summary")



class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("app1:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model=Item
    paginate_by=10
    template_name="index.html"
    def get_queryset(self):
        return Item.objects.order_by('slug')[:6]

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
                'object':order
            }
            return render(self.request,"order_summary.html",context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class ItemDetailView(DetailView):
    model=Item
    template_name="product-page.html"
@login_required
def add_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_item, created=OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"This item Quantity was Updated")
            return redirect("app1:products",slug=slug )
        else:
            order.items.add(order_item)
            messages.info(request,"This item was added to your cart")
            return redirect("app1:products",slug=slug)
    else:
        ordered_date= timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item was added to your cart")
    return redirect("app1:products",slug=slug)

@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request,"This item was removed from your cart")
            return redirect("app1:order_summary")
        else:
            messages.info(request,"This item was not in your cart")
            return redirect("app1:products",slug=slug)
    else:
        messages.info(request,"You do not have an active order")
        return redirect("app1:products",slug=slug)

@login_required
def remove_single_item_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,"This item was updated in your cart")
            return redirect("app1:order_summary")
        else:
            messages.info(request,"This item was not in your cart")
            return redirect("app1:products",slug=slug)
    else:
        messages.info(request,"You do not have an active order")
        return redirect("app1:products",slug=slug)



def products(request):
    context={
        'items':Item.objects.all()
    }
    return render(request,'product-page.html',context)

def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request,"This Coupon does not Exist")
        return redirect("app1:checkout")
def success(request):
    order=Order.objects.all()
    order.delete()
    return render(request,'success.html')

class AddCouponView(View):
    def post(self,*args,**kwargs):
        if self.request.method == 'POST':
            form=CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code=form.cleaned_data.get('code')
                    order=Order.objects.get(user=self.request.user,ordered=False)
                    order.coupon=get_coupon(self.request,code)
                    order.save()
                    messages.success(self.request,"Successfully Added Coupon")
                    return redirect("app1:checkout")
                except ObjectDoesNotExist:
                    messages.info(self.request,"You do not have active Order")
                    return redirect("app1:checkout")

class RequestRefundView(View):
    def get(self,*args,**kwargs):
        form = RefundForm()
        context={
            'form':form,
        }
        return render(self.request,"request_refund.html",context)
    def post(self,*args,**kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code= form.cleaned_data.get('ref_code')
            message= form.cleaned_data.get('message')
            email= form.cleaned_data.get('email')
            try:
                order=Order.objects.get(ref_code=ref_code)
                order.refund_requested=True
                order.save()

                refund=Refund()
                refund.order=order
                refund.reason=message
                refund.email=email
                refund.save()
                messages.info(self.request,"Your Message was Recived")
                return redirect("app1:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request,"This order Does not Exist")
                return redirect("app1:request-refund")


def Signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f'Account Created For {username}!')
            return HttpResponseRedirect('/accounts/login')
    else:
        form=SignupForm()
    return render(request,'signup.html',{'form':form})

def logout_view(request):
    return render(request,'logout.html')
