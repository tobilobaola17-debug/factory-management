

from .models import Product, RawMaterial, UserProfile
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout
from decimal import Decimal, InvalidOperation
from .models import Product, RawMaterial, StockMovement, UserProfile
from .models import (
     Customer,
     Order,
     OrderItem,
     Product,
    ProductionRun,
     RawMaterial, 
     StockMovement, 
     Supplier,
)
from django.db.models import Q
from datetime import date
from django.db.models import Sum
from functools  import wraps
from .models import Supplier, RawMaterial
from django.shortcuts import get_object_or_404


def custom_login_view(request):
  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect('dashboard')
  else:
    form = AuthenticationForm()
  return render(request, 'login.html', {'form': form})


@login_required
def dashboard_view(request):
  profile, created = UserProfile.objects.get_or_create(
    user=request.user,
    defaults={'role': 'admin' if request.user.is_superuser else 'staff'},
  )
  user_role = profile.role

  products_count = Product.objects.count()
  raw_materials = RawMaterial.objects.all() 
  low_stock_items = [rm for rm in raw_materials if rm.is_low_stock()]
  context = {
      'role': user_role,
      'product_count': products_count,
      'raw_materials': raw_materials,
      'low_stock_items': low_stock_items,
  }
  return render(request, 'dashboard.html', context)


@login_required
def raw_material_list_view(request):
  materials = RawMaterial.objects.select_related('supplier').order_by('name')
  return render(request, 'raw_material.html', {'materials': materials})


@login_required
def record_stock_movement_view(request, pk):
  material = get_object_or_404(RawMaterial, pk=pk)
  suppliers = Supplier.objects.all().order_by('name')
  error = None

  if request.method == 'POST':
    movement_type = request.POST.get('movement_type')
    try:
      quantity = Decimal(request.POST.get('quantity', ''))
    except InvalidOperation:
      error = 'Enter a valid quantity.'
    else:
      if not quantity.is_finite() or quantity <= 0:
        error = 'Quantity must be greater than zero.'
      elif movement_type not in {'IN', 'OUT'}:
        error = 'Choose a valid movement type.'
      elif movement_type == 'OUT' and quantity > material.current_quantity:
        error = 'There is not enough stock for this movement.'
      else:
        supplier_id = request.POST.get('supplier')
        supplier = (
            get_object_or_404(Supplier, pk=supplier_id)
            if movement_type == 'IN' and supplier_id
            else None
        )
        if movement_type == 'IN':
          material.current_quantity += quantity
          if supplier:
            material.supplier = supplier
        else:
          material.current_quantity -= quantity
        material.save()
        StockMovement.objects.create(
            material=material,
            movement_type=movement_type,
            quantity=quantity,
            supplier=supplier,
            notes=request.POST.get('notes', '').strip(),
        )
        return redirect('raw_material_list')

  return render(
      request,
      'record_stock.html',
      {'material': material, 'suppliers': suppliers, 'error': error},
  )

@login_required
def update_stock_view(request, pk):
  item = get_object_or_404(RawMaterial, pk=pk)

  if request.method == 'POST':
    new_quantity = request.POST.get('current_quantity')
    if new_quantity:
      item.current_quantity = int(new_quantity)
      item.save()
      return redirect('dashboard')

  return render(request, 'update_stock.html', {'item': item})

@login_required
def products_view(request):
  profile, created = UserProfile.objects.get_or_create(
      user=request.user,
      defaults={'role': 'admin' if request.user.is_superuser else 'staff'},
  )
  products = Product.objects.all()
  context = {
      'products': products,
      'role': profile.role,
  }
  return render(request, 'products.html', context)

@login_required
def add_raw_material_view(request):
  materials = RawMaterial.objects.all()
  return render(request, 'raw_materials.html', {'materials': materials}),

  if request.method == 'POST':
    name = request.POST.get('name')
    current_quantity = request.POST.get('current_quantity')
    minimum_level = request.POST.get('minimum_level')
    unit = request.POST.get('unit')

    if name and current_quantity and minimum_level and unit:
      RawMaterial.objects.create(
          name=name,
          current_quantity=int(current_quantity),
          minimum_level=int(minimum_level),
          unit=unit,
      )
      return redirect('dashboard')

  return render(request, 'add_raw_material.html')

def custom_logout_view(request):
  logout(request)
  return redirect('login')

@login_required
def stock_movement_view(request, pk):
  item = get_object_or_404(RawMaterial, pk=pk)
  error = None

  if request.method == 'POST':
    movement_type = request.POST.get('movement_type')
    qty_str = request.POST.get('quantity')
    supplier_id = request.POST.get('supplier')

    if qty_str and qty_str.isdigit():
      qty = int(qty_str)

      if qty > 0:
        if movement_type == 'IN':
          supplier_obj = (
            Supplier.objects.get(id=supplier_id) if supplier_id else None
          )
          item.current_quantity += qty
          item.save()
          StockMovement.objects.create(
              material=item,
              movement_type='IN',
              quantity=qty,
              user=request.user,
              supplier=supplier_obj,
          )
          return redirect('dashboard')

        elif movement_type == 'OUT':
          if item.current_quantity >= qty:
            item.current_quantity -= qty
            item.save()
            StockMovement.objects.create(
                material=item,
                movement_type='OUT',
                quantity=qty,
                user=request.user,

            )
            return redirect('dashboard')
          else:
            error = (
                f'Cannot remove {qty}. Only {item.current_quantity}'
                f' {item.unit} available!'
            )
      else:
        error = 'Quantity must be greater than zero.'

  return render(
      request, 'stock_movement.html',
        {'item': item, 'suppliers': suppliers, 'error': error},
  )


@login_required
def production_list_view(request):
  profile, created = UserProfile.objects.get_or_create(
      user=request.user,
      defaults={'role': 'admin' if request.user.is_superuser else 'staff'},
  )
  runs = ProductionRun.objects.all().order_by('-date')
  products = Product.objects.all()
  context = {
      'runs': runs,
      'products': products,
      'role': profile.role,
  }
  return render(request, 'production_list.html', context)


@login_required
def add_production_run_view(request):
  if request.method == 'POST':
    product_id = request.POST.get('product')
    quantity = int(request.POST.get('quantity_produced'))
    status = request.POST.get('status')

    product = get_object_or_404(Product, id=product_id)

    run = ProductionRun.objects.create(
        product=product,
        quantity_produced=quantity,
        status=status,
        supervisor=request.user,
    )

    # If completed right away, increment finished goods stock!
    if status == 'Completed':
      product.current_quantity += quantity
      product.save()

    return redirect('production_list')

  products = Product.objects.all()
  return render(
      request, 'add_production_run.html', {'products': products}
  )
@login_required
def add_product_view(request):
  if request.method == 'POST':
    name = request.POST.get('name')
    code = request.POST.get('code')
    category = request.POST.get('category')
    unit = request.POST.get('unit')
    price = request.POST.get('price')
    current_quantity = request.POST.get('current_quantity', 0)

    if name and code and category:
      Product.objects.create(
          name=name,
          code=code,
          category=category,
          unit=unit if unit else 'pcs',
          price=price if price else 0.00,
          current_quantity=int(current_quantity) if current_quantity else 0,
      )
      return redirect('products')

  return render(request, 'add_product.html')

@login_required
def supplier_list_view(request):
  suppliers = Supplier.objects.all()
  return render(request, 'supplier_list.html', {'suppliers': suppliers})


@login_required
def add_supplier_view(request):
  if request.method == 'POST':
    name = request.POST.get('name')
    contact = request.POST.get('contact')
    material_ids = request.POST.getlist('materials')

    if name :
      supplier = Supplier.objects.create(name=name, contact_info=contact)
    if material_ids:
        RawMaterial.objects.filter(id__in=material_ids).update(supplier=supplier) 
      
    return redirect('supplier_list')
  
  materials = RawMaterial.objects.all()
  return render(request, 'add_supplier.html', {'materials': materials})

from .models import Customer, Order, OrderItem


@login_required
def order_list_view(request):
  orders = Order.objects.all().order_by('-order_date')
  return render(request, 'order_list.html', {'orders': orders})


@login_required
def add_order_view(request):
  if request.method == 'POST':
    customer_id = request.POST.get('customer')
    product_id = request.POST.get('product')
    quantity = int(request.POST.get('quantity', 1))

    if customer_id and product_id:
      customer = Customer.objects.get(id=customer_id)
      product = Product.objects.get(id=product_id)
      unit_price = product.price  # Uses the product's price

      # Create the order
      order = Order.objects.create(
          customer=customer, total_amount=unit_price * quantity
      )

      # Create the order item
      OrderItem.objects.create(
          order=order, product=product, quantity=quantity, unit_price=unit_price
      )

      return redirect('order_list')

  customers = Customer.objects.all()
  products = Product.objects.all()
  return render(
      request,
      'add_order.html',
      {'customers': customers, 'products': products},
  )

from django.contrib import messages
from .models import Customer, Order, OrderItem


@login_required
def order_list_view(request):
  orders = Order.objects.all().order_by('-order_date')
  return render(request, 'order_list.html', {'orders': orders})


@login_required
def add_order_view(request):
  if request.method == 'POST':
    customer_name = request.POST.get('customer_name', '').strip()
    product_ids = request.POST.getlist('products[]')
    quantities = request.POST.getlist('quantities[]')

    if customer_name and product_ids:
      customer, created = Customer.objects.get_or_create(name=customer_name)

    
      order = Order.objects.create(customer=customer, total_amount=0)
      total_amount = Decimal('0.00')

    
      for prod_id, qty_str in zip(product_ids, quantities):
        if prod_id and qty_str:
          product = Product.objects.get(id=prod_id)
          quantity = int(qty_str)
          unit_price = product.price

          
          OrderItem.objects.create(
              order=order,
              product=product,
              quantity=quantity,
              unit_price=unit_price,
          )

          total_amount += unit_price * quantity

      
      order.total_amount = total_amount
      order.save()

      messages.success(request, f'Order #{order.id} created successfully!')
      return redirect('order_list')

  products = Product.objects.all()
  return render(
      request, 'add_order.html', {'products': products})
  


@login_required
def dispatch_order_view(request, pk):
  order = Order.objects.get(pk=pk)

  if order.status == 'Pending':
    # 1. First, validate if ALL items have enough stock
    for item in order.items.all():
      if item.product.current_quantity < item.quantity:
        messages.error(
            request,
            f'Cannot dispatch! Insufficient stock for {item.product.name}.'
            f' Required: {item.quantity}, Available:'
            f' {item.product.current_quantity}',
        )
        return redirect('order_list')

    
    for item in order.items.all():
      product = item.product
      product.current_quantity -= item.quantity
      product.save()

    order.status = 'Dispatched'
    order.save()
    messages.success(request, f'Order #{order.id} successfully dispatched!')

  return redirect('order_list')



@login_required
def product_list_view(request):
  query = request.GET.get('q', '')
  if query:
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(code__icontains=query)
    )
  else:
    products = Product.objects.all()
  return render(request, 'products.html', {'products': products, 'query': query})


@login_required
def edit_product_view(request, pk):
  product = Product.objects.get(pk=pk)
  if request.method == 'POST':
    product.name = request.POST.get('name')
    product.code = request.POST.get('code', '')
    product.category = request.POST.get('category', '')
    product.unit = request.POST.get('unit', '')
    product.price = request.POST.get('price')
    product.current_quantity = request.POST.get('current_quantity')
    product.save()
    messages.success(
        request, f'Product "{product.name}" updated successfully!'
    )
    return redirect('products')

  return render(request, 'edit_product.html', {'product': product})


@login_required
def delete_product_view(request, pk):
  product = Product.objects.get(pk=pk)
  product_name = product.name
  product.delete()
  messages.success(request, f'Product "{product_name}" deleted successfully!')
  return redirect('products')


@login_required
def dashboard_view(request):
  # 1. Key Totals & Metrics
  total_products = Product.objects.count()
  pending_orders_count = Order.objects.filter(status='Pending').count()

  # Low-stock items count
  low_stock_materials = [
      m for m in RawMaterial.objects.all() if m.is_low_stock
  ]
  low_stock_count = len(low_stock_materials)

  # Today's production count/records
  today = date.today()
  todays_production = ProductionRun.objects.filter(date__date=today)
  todays_production_count = todays_production.count()

  # 2. Date-Filtered Reports
  start_date = request.GET.get('start_date')
  end_date = request.GET.get('end_date')

  production_reports = ProductionRun.objects.all().order_by('-date')
  stock_movements = StockMovement.objects.all().order_by('-date')

  if start_date and end_date:
    production_reports = production_reports.filter(
        date__range=[start_date, end_date]
    )
    stock_movements = stock_movements.filter(
        date__date__range=[start_date, end_date]
    )

  context = {
      'total_products': total_products,
      'pending_orders_count': pending_orders_count,
      'low_stock_count': low_stock_count,
      'todays_production_count': todays_production_count,
      'low_stock_materials': low_stock_materials,
      'production_reports': production_reports,
      'stock_movements': stock_movements,
      'start_date': start_date or '',
      'end_date': end_date or '',
  }
  return render(request, 'dashboard.html', context)

def role_required(allowed_roles=[]):
  def decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
      if not request.user.is_authenticated:
        return redirect('login')
      # Superusers / Admins always have access
      if request.user.is_superuser or (
          hasattr(request.user, 'profile')
          and request.user.profile.role == 'admin'
      ):
        return view_func(request, *args, **kwargs)

      # Check if user's role is in allowed roles
      if (
          hasattr(request.user, 'profile')
          and request.user.profile.role in allowed_roles
      ):
        return view_func(request, *args, **kwargs)

      messages.error(
          request, 'Access Denied: You do not have permission for this action.'
      )
      return redirect('dashboard')

    return _wrapped_view

  return decorator

def delete_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'confirm_delete.html', {'supplier': supplier})
