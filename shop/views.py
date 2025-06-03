from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .forms import OrderUpdateForm  
from .models import Product, Contact, Orders, OrderUpdate
from django.contrib.auth.models import User
from django.contrib import messages
from math import ceil
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';   
from django.utils.dateparse import parse_date
from django.db.models import Sum
from .models import Advertise
from .forms import AdvertiseForm



from django.core.mail import send_mail
from django.conf import settings


from .forms import TableForm   
from .models import Table
from django.contrib.auth.decorators import login_required



from decimal import Decimal

from .models import Orders, Product
from .forms import OrderUpdateForm

# # Import Checksum utility for Paytm integration
# try:
#     from .Paytm import Checksum  # Use relative import for local Paytm module
# except ImportError:
#     # If the Paytm Checksum utility is not found, raise an explicit error
#     raise ImportError("Paytm Checksum module not found. Please ensure 'Paytm/Checksum.py' exists in your app directory.")

# Custom JSON encoder to handle Decimal objects


from django.db.models import Sum
from collections import defaultdict

def get_purchased_quantities():
    orders = Orders.objects.all()
    quantities = defaultdict(int)
    for order in orders:
        items = json.loads(order.items_json)
        for item_id, item_data in items.items():
            quantity = item_data[0]
            product_name = item_data[1]
            quantities[product_name] += quantity
    return quantities



class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return super(DecimalEncoder, self).default(obj)


from .forms import OrderUpdateForm, AdvertiseForm, TableForm, GroceryItemForm
from .models import Product, Contact, Orders, OrderUpdate, Advertise, Table, GroceryItem

@login_required
def grocery_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id', '')
        if 'delete' in request.POST:
            # Delete item
            item = get_object_or_404(GroceryItem, id=item_id)
            item.delete()
            messages.success(request, f"{item.name} deleted successfully.")
            return redirect('shop:grocery_view')
        else:
            # Add or update item
            form = GroceryItemForm(request.POST, instance=GroceryItem.objects.get(id=item_id) if item_id else None)
            if form.is_valid():
                item = form.save()
                action = "updated" if item_id else "added"
                messages.success(request, f"Item {item.name} {action} successfully.")
                return redirect('shop:grocery_view')
            else:
                messages.error(request, "Error in form submission. Please check the data.")

    else:
        form = GroceryItemForm()

    grocery_items = GroceryItem.objects.all().order_by('-timestamp')
    total_price_sum = grocery_items.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'shop/grocery.html', {
        'form': form,
        'grocery_items': grocery_items,
        'total_price_sum': total_price_sum,
    })

# Existing views (unchanged, included for completeness)
def update_order(request, order_id):
    order = get_object_or_404(Orders, order_id=order_id)
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.items_json = request.POST.get('itemsJson')
            updated_order.amount = request.POST.get('amount')
            updated_order.save()
            product_ids = json.loads(updated_order.items_json)
            product_names = ', '.join(
                Product.objects.get(id=prod_id).product_name for prod_id in product_ids.keys()
            )
            messages.success(request, f"Order {order_id} successfully updated. Products: {product_names} with amount Rs. {updated_order.amount}.")
            return redirect('shop:orderView')
    else:
        form = OrderUpdateForm(instance=order)
    form_data_json = {field: form.initial.get(field, '') for field in form.fields}
    cart_data = json.loads(order.items_json) if order.items_json else {}
    products = Product.objects.all().order_by('product_name')
    return render(request, 'shop/update_order.html', {
        'form': form,
        'form_data_json': json.dumps(form_data_json, cls=DecimalEncoder),
        'cart_data_json': json.dumps(cart_data, cls=DecimalEncoder),
        'products': products,
        'order': order
    })




def update_order(request, order_id):
    # Retrieve the order instance or return a 404 error if not found
    order = get_object_or_404(Orders, order_id=order_id)

    if request.method == 'POST':
        # Create a form instance with POST data
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            # Save the form data without committing to the database yet
            updated_order = form.save(commit=False)
            # Update the items_json and amount from the POST request
            updated_order.items_json = request.POST.get('itemsJson')  # Ensure you are using 'itemsJson'
            updated_order.amount = request.POST.get('amount')
            # Save the updated order to the database
            updated_order.save()

            # Retrieve product names associated with the order
            product_ids = json.loads(updated_order.items_json)  # Use updated_order's items_json
            product_names = ', '.join(
                Product.objects.get(id=prod_id).product_name for prod_id in product_ids.keys()
            )

            # Add a success message for the user
            messages.success(request, f"Order {order_id} successfully updated. Products: {product_names} with amount Rs. {updated_order.amount}.")
            # Redirect to the order view
            return redirect('shop:orderView')
    else:
        # Prepare the form with existing order data for GET requests
        form = OrderUpdateForm(instance=order)

    # Prepare form data and cart data in JSON format
    form_data_json = {field: form.initial.get(field, '') for field in form.fields}
    cart_data = json.loads(order.items_json) if order.items_json else {}

    # Retrieve all products to display them in the template
    products = Product.objects.all().order_by('product_name')

    return render(request, 'shop/update_order.html', {
        'form': form,
        'form_data_json': json.dumps(form_data_json, cls=DecimalEncoder),  # Use custom encoder
        'cart_data_json': json.dumps(cart_data, cls=DecimalEncoder),        # Convert cart data to JSON
        'products': products,  # Pass all products to the template
        'order': order  # Pass the order object to the template
    })





@login_required
def inventory_view(request):
    # Filter products by category "Drinks"
    drinks = Product.objects.filter(category="Drinks")
    
    # Check for low stock and prepare notifications
    low_stock_products = [drink for drink in drinks if drink.stock_quantity <= drink.low_stock_threshold]
    
    if low_stock_products:
        messages.warning(request, "Low stock alert for: " + ", ".join([p.product_name for p in low_stock_products]))

    return render(request, 'shop/inventory.html', {
        'drinks': drinks,
        'low_stock_products': low_stock_products,
    })



@login_required
def table_page(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:table_page')
    else:
        form = TableForm()


    tables = Table.objects.all().order_by('number')

    return render(request, 'shop/table.html', {'form': form, 'tables': tables})


@login_required
def orderView(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Redirect to the index page if the user is not authenticated
        messages.warning(request, "You must be logged in to view this page.")
        return redirect('index')  # 'index' is the name of the URL pattern for the homepage
    
    current_user = request.user

    # Check if the user's last name is "admin"
    if current_user.last_name.lower() == "admin":
        orderHistory = Orders.objects.all()  # Show all orders for admin
    else:
        orderHistory = Orders.objects.filter(userId=current_user.id)  # Show only the user's orders

    # Initialize totals
    total_amount = 0
    cash_total = 0
    card_total = 0
    online_total = 0
    other_total = 0

    # Get selected payment method and table number from POST data
    selected_payment_method = request.POST.get('payment_method', '')
    selected_table_no = request.POST.get('table_no', '')

    # If the user submits a date filter via POST
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            # Filter the order history by the provided date range
            orderHistory = orderHistory.filter(timestamp__date__range=(start_date, end_date))

        # Filter by payment method if one is selected
        if selected_payment_method:
            orderHistory = orderHistory.filter(payment_method__iexact=selected_payment_method)

        # Filter by table number if one is provided
        if selected_table_no:
            orderHistory = orderHistory.filter(table_number__iexact=selected_table_no)

    # Calculate totals for each payment method
    cash_total = orderHistory.filter(payment_method__iexact='cash').aggregate(total=Sum('amount'))['total'] or 0
    card_total = orderHistory.filter(payment_method__iexact='card').aggregate(total=Sum('amount'))['total'] or 0
    online_total = orderHistory.filter(payment_method__iexact='online').aggregate(total=Sum('amount'))['total'] or 0
    other_total = orderHistory.filter(payment_method__iexact='other').aggregate(total=Sum('amount'))['total'] or 0

    # Calculate the total amount for all filtered orders
    total_amount = orderHistory.aggregate(total=Sum('amount'))['total'] or 0

    # If no orders are found, inform the user
    if not orderHistory.exists():
        messages.info(request, "No orders found with the selected filters.")
        return render(request, 'shop/orderView.html')

    # Render the template with order history and totals for each payment method
    return render(request, 'shop/orderView.html', {
        'orderHistory': orderHistory,
        'total_amount': total_amount,
        'cash_total': cash_total,
        'card_total': card_total,
        'online_total': online_total,
        'other_total': other_total,
        'selected_table_no': selected_table_no,
    })


@login_required
def save(request):
    if request.method == "POST":
        # Debugging: Print all POST data
        print(f"POST Data: {request.POST}")

        if 'order_lookup' in request.POST:
            # Handle order lookup by order_id
            order_id = request.POST.get('order_id', '')
            try:
                order = Orders.objects.get(order_id=order_id)
                order_updates = OrderUpdate.objects.filter(order_id=order_id)
                items_json = json.loads(order.items_json)  # Assuming items_json is a JSON string
                return render(request, 'shop/index1.html', {
                    'order': order,
                    'order_updates': order_updates,
                    'order_found': True,
                    'items': items_json
                })
            except Orders.DoesNotExist:
                return render(request, 'shop/index1.html', {'order_not_found': True})

        else:
            # Handle the standard checkout process
            user_id = request.POST.get('user_id', '')
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')

            # Debugging: Print received user_id
            print(f"Received User ID: {user_id}")

            if not user_id:
                messages.error(request, 'User ID is required.')
                return redirect('shop:index')

            try:
                user_id = int(user_id)
            except ValueError:
                messages.error(request, 'Invalid User ID.')
                return redirect('shop:index')

            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            phone = request.POST.get('phone', '9172353945')  # Default phone if none is provided
            items_json = request.POST.get('itemsJson', '')
            amount = request.POST.get('amount', '')
            order_action = request.POST.get('order_action', 'new')
            payment_method = request.POST.get('payment_method', '')  # Capture payment method
            payment_comments = request.POST.get('payment_comments', '')  # Capture payment comments

            # Validate and convert amount
            try:
                amount = float(amount) if amount else 0.0
                print(f"Processed Amount: {amount}")  # Debugging: Print processed amount
            except ValueError:
                messages.error(request, 'Invalid amount.')
                return redirect('shop:index')

            # Validate payment method and comments
            if payment_method == 'other' and not payment_comments:
                messages.error(request, 'Payment comments are required for the "Other" payment method.')
                return redirect('shop:checkout')

            # Store customer data in session
            request.session['customer_data'] = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'address': address,
                'phone': phone,
                'payment_method': payment_method,
                'payment_comments': payment_comments
            }

            if order_action == 'update':
                order_id = request.POST.get('order_id', '')
                try:
                    order = Orders.objects.get(order_id=order_id, userId=user_id)
                    # Update fields
                    order.items_json = items_json
                    order.address = address
                    order.phone = phone
                    order.amount = amount
                    order.name = name
                    order.email = email
                    order.city = city
                    order.state = state
                    order.zip_code = zip_code
                    order.payment_method = payment_method  # Update payment method
                    order.payment_comments = payment_comments  # Update payment comments if 'Other'
                    order.save()

                    update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Updated")
                    update.save()

                    messages.success(request, f"Order {order.order_id} successfully updated.")
                    return redirect('shop:orderView')  # Redirect to order view

                except Orders.DoesNotExist:
                    messages.error(request, 'Order not found or invalid.')
                    return redirect('shop:index')

            else:
                # Create a new order
                order = Orders(
                    items_json=items_json,
                    userId=user_id,
                    address=address,
                    phone=phone,
                    amount=amount,
                    name=name,
                    email=email,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    payment_method=payment_method,  # Set payment method
                    payment_comments=payment_comments  # Set payment comments if 'Other'
                )
                order.save()

                update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
                update.save()

                messages.success(request, f"Order {order.order_id} successfully created.")
                return redirect('shop:orderView')  # Redirect to order view

            # Handle payment options
            if 'onlinePay' in request.POST:
                # Handle online payment
                darshan_dict = {
                    'MID': 'WorldP64425807474247',  # Your Merchant ID
                    'ORDER_ID': str(order.order_id),
                    'TXN_AMOUNT': str(amount),
                    'CUST_ID': '',  # Removed email
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
                }
                darshan_dict['CHECKSUMHASH'] = Checksum.generate_checksum(darshan_dict, MERCHANT_KEY)
                return render(request, 'shop/paytm.html', {'darshan_dict': darshan_dict})

            elif 'cashOnDelivery' in request.POST:
                return redirect('shop:orderView')

    return render(request, 'shop/index1.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F  # Import F to fix the NameError
from .models import Product

@login_required
def index(request, table_number):
    # Initialize an empty list to hold all products
    allProds = []
    
    # Get distinct categories and subcategories
    categories = Product.objects.values('category', 'subcategory').distinct()
    cats = {item['category'] for item in categories}
    
    # Loop through categories and subcategories to group products
    for cat in cats:
        subcats = {item['subcategory'] for item in categories if item['category'] == cat}
        cat_prods = []
        
        for subcat in subcats:
            # Filter products by category and subcategory
            prod = Product.objects.filter(category=cat, subcategory=subcat)
            cat_prods.append([subcat, prod])
        
        allProds.append([cat, cat_prods])
    
    # Get low stock products for drinks
    low_stock_products = Product.objects.filter(
        category="Drinks",
        stock_quantity__lte=F('low_stock_threshold')  # Use F instead of models.F
    )
    
    # Add warning messages for low stock products
    if low_stock_products:
        messages.warning(request, "Low stock alert for: " + ", ".join([p.product_name for p in low_stock_products]))

    context = {
        'allProds': allProds,
        'table_number': table_number,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'shop/index1.html', context)
    
@login_required
def advertise(request):
    if request.method == 'POST':
        form = AdvertiseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('about')  # Redirect to the about page or another relevant page
    else:
        form = AdvertiseForm()
    return render(request, 'shop/advertise.html', {'form': form})

def about(request):
    advertisements = Advertise.objects.all()  # Get all advertisements
    return render(request, 'shop/about.html', {'advertisements': advertisements})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')

        # Validate data if needed

        # Prepare the email content
        subject = f"Contact Form Royal Shetkari from {name}"
        message = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {desc}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['yalmarprasad123@gmail.com']

        # Send email
        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Thanks for contacting us. We will get back to you soon!')
            return redirect('shop:contact')  # Redirect back to contact page
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again later.')

    return render(request, 'shop/contact.html')

@login_required
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        
        try:
            # Filter order by order_id only
            order = Orders.objects.filter(order_id=orderId)
            if order.exists():
                # Fetch updates related to the order
                updates = []
                update_items = OrderUpdate.objects.filter(order_id=orderId)
                for item in update_items:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                
                response = json.dumps({
                    "status": "success", 
                    "updates": updates, 
                    "itemsJson": order[0].items_json
                }, default=str)
                
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    
    return render(request, 'shop/tracker.html')


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.desc or query in item.product_name or query in item.category or query in item.desc.upper() or query in item.product_name.upper() or query in item.category.upper():
        return True
    else:
        return False
def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'subcategory', 'id')
    cats = {item['category'] for item in catprods}
    cart = request.session.get('cart', {})

    for cat in cats:
        subcats = {item['subcategory'] for item in catprods if item['category'] == cat}
        subcat_prods = []
        for subcat in subcats:
            prodtemp = Product.objects.filter(category=cat, subcategory=subcat)
            prod = [item for item in prodtemp if searchMatch(query, item) and str(item.id) not in cart]
            if len(prod) != 0:
                subcat_prods.append((subcat, prod))
        
        if len(subcat_prods) != 0:
            allProds.append((cat, subcat_prods))
        else:
            # If no subcategories, display products directly under the category
            prodtemp = Product.objects.filter(category=cat)
            prod = [item for item in prodtemp if searchMatch(query, item) and str(item.id) not in cart]
            if len(prod) != 0:
                allProds.append((cat, [("", prod)]))
    
    context = {'allProds': allProds, 'cart': cart, "msg": ""}
    if len(allProds) == 0 or len(query) < 3:
        context = {'msg': "No item available. Please make sure to enter relevant search query"}
    
    return render(request, 'shop/search.html', context)




def productView(request, myid):
    product = get_object_or_404(Product, product_id=myid)  # Use product_id as per your model
    cart = request.session.get('cart', {})
    
    # Check if the product has low stock
    low_stock = product.stock_quantity <= product.low_stock_threshold
    if low_stock:
        messages.warning(request, f"Low stock alert for {product.product_name}! Only {product.stock_quantity} remaining.")

    if request.method == 'POST':
        qty = int(request.POST.get('qty', 1))
        
        # Validate stock availability
        if qty > product.stock_quantity:
            messages.error(request, f"Cannot add {qty} units of {product.product_name}. Only {product.stock_quantity} available.")
            return redirect('shop:productView', myid=myid)

        # Update cart
        if str(myid) in cart:
            cart[str(myid)][0] += qty
        else:
            cart[str(myid)] = [qty, product.product_name, product.price]
        request.session['cart'] = cart
        messages.success(request, f"{qty} unit(s) of {product.product_name} added to cart")

        # Optionally deduct stock here if you want to reserve it (or handle in checkout)
        # product.stock_quantity -= qty
        # product.save()

        return redirect('shop:productView', myid=myid)

    return render(request, 'shop/prodView.html', {
        'product': product,
        'low_stock': low_stock,
        'stock_quantity': product.stock_quantity,
        'low_stock_threshold': product.low_stock_threshold,
    })

def handeLogin(request):
    if request.method == "POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "Invalid credentials! Please try again")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("404- Not found")



    
def handleSignUp(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']  # Dropdown value
        email = request.POST['email1']
        phone = request.POST['phone']
        password = request.POST['password']
        password1 = request.POST['password1']

        # Validate if the last name (role) is one of the predefined options
        allowed_roles = ["admin", "manager", "employee"]
        if l_name not in allowed_roles:
            messages.warning(request, "Invalid role selected.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Check if passwords match
        if password1 != password:
            messages.warning(request, "Passwords do not match")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Check if username is already taken
        try:
            user = User.objects.get(username=username)
            messages.warning(request, "Username already taken. Try a different one.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except User.DoesNotExist:
            # Create the user if all validations pass
            myuser = User.objects.create_user(username=username, email=email, password=password)
            myuser.first_name = f_name
            myuser.last_name = l_name  # Store the role in last_name
            myuser.phone = phone
            myuser.save()
            messages.success(request, "Your account has been successfully created")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("404 - Not found")



def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('index')  # Redirects to the homepage

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})


