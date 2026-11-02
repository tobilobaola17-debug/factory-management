from dataclasses import Field

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
  ROLE_CHOICES = (
      ('admin', 'Admin'),
      ('manager', 'Manager'),
      ('staff', 'Staff'),
  )
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')

  def __str__(self):
    return f'{self.user.username} - {self.role}'


class RawMaterial(models.Model):
  name = models.CharField(max_length=100)
  current_quantity = models.IntegerField(default=0)
  minimum_level = models.IntegerField(default=10)
  unit = models.CharField(max_length=20, default='kg')  # e.g., kg, pieces, liters

  def is_low_stock(self):
    return self.current_quantity < self.minimum_level

  def __str__(self):
    return f'{self.name} ({self.current_quantity} {self.unit})'


class Product(models.Model):
  name = models.CharField(max_length=100)
  code = models.CharField(max_length=50, unique=True)
  unit = models.CharField(max_length=20, default='pcs')
  category = models.CharField(max_length=50, blank=True, null=True)
  price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

  def __str__(self):
    return self.name
class StockMovement(models.Model):
  MOVEMENT_TYPES = (
      ('IN', 'Stock In (Received)'),
      ('OUT', 'Stock Out (Used)'),
  )

  material = models.ForeignKey(
      RawMaterial, on_delete=models.CASCADE, related_name='movements'
  )
  movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
  quantity = models.PositiveIntegerField()
  date = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  supplier = models.ForeignKey(
    'Supplier', on_delete=models.SET_NULL, null=True, blank=True
  )

  def __str__(self):
    return f'{self.movement_type} - {self.quantity} {self.material.unit} of {self.material.name}'

  
class Product(models.Model):
  name = models.CharField(max_length=100)
  code = models.CharField(max_length=50, unique=True)
  category = models.CharField(max_length=100)
  unit = models.CharField(max_length=20, default='pcs')
  price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  current_quantity = models.PositiveIntegerField(default=0)
      
   

  def __str__(self):
    return f'{self.name} ({self.code})'
class StockMovement(models.Model):
  MOVEMENT_TYPES = (
      ('IN', 'Stock In (Received)'),
      ('OUT', 'Stock Out (Used)'),
  )

  material = models.ForeignKey(
      RawMaterial, on_delete=models.CASCADE, related_name='movements'
  )
  movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
  quantity = models.PositiveIntegerField()
  date = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  supplier = models.ForeignKey(
      'Supplier', on_delete=models.SET_NULL, null=True, blank=True
)
  def __str__(self):
    return f'{self.movement_type} - {self.quantity} of {self.material.name}'  

class ProductionRun(models.Model):
  STATUS_CHOICES = (
      ('Planned', 'Planned'),
      ('In Progress', 'In Progress'),
      ('Completed', 'Completed'),
  )

  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity_produced = models.PositiveIntegerField()
  date = models.DateTimeField(auto_now_add=True)
  supervisor = models.ForeignKey(
      User, on_delete=models.SET_NULL, null=True, blank=True
  )
  status = models.CharField(
      max_length=20, choices=STATUS_CHOICES, default='Planned'
  )

  def __str__(self):
    return (
        f'Run #{self.id} - {self.product.name} ({self.quantity_produced}'
        f' {self.product.unit}) [{self.status}]'
    ) 
    
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    #supplied_materials = models.ManyToManyField('RawMaterial', blank=True)
    

def __str__(self):
  return self.name

class Customer(models.Model):
  name = models.CharField(max_length=100)
  email = models.EmailField(blank=True, null=True)
  phone = models.CharField(max_length=20)
  address = models.TextField(blank=True)

  def __str__(self):
    return self.name


class Order(models.Model):
  STATUS_CHOICES = (
      ('Pending', 'Pending'),
      ('Dispatched', 'Dispatched'),
      ('Cancelled', 'Cancelled'),
  )

  customer = models.ForeignKey(
      Customer, on_delete=models.CASCADE, related_name='orders'
  )
  order_date = models.DateTimeField(auto_now_add=True)
  status = models.CharField(
      max_length=20, choices=STATUS_CHOICES, default='Pending'
  )
  total_amount = models.DecimalField(
      max_digits=12, decimal_places=2, default=0.00
  )

  def __str__(self):
    return f'Order #{self.id} - {self.customer.name} [{self.status}]'


class OrderItem(models.Model):
  order = models.ForeignKey(
      Order, on_delete=models.CASCADE, related_name='items'
  )
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)

  def get_total(self):
    return self.quantity * self.unit_price

  def __str__(self):
    return f'{self.quantity}x {self.product.name} (Order #{self.order.id})'  

class RawMaterial(models.Model):
  name = models.CharField(max_length=100)
  code = models.CharField(
      max_length=50, unique=True, blank=True, null=True
  )  
  current_quantity = models.DecimalField(
      max_digits=10, decimal_places=2, default=0
  )
  minimum_stock_level = models.DecimalField(
      max_digits=10, decimal_places=2, default=10
  )  
  unit = models.CharField(max_length=50, default='units')
  supplier = models.ForeignKey(
      'Supplier',
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='materials',
  )

  def __str__(self):
    return self.name

  @property
  def is_low_stock(self):
    return self.current_quantity < self.minimum_stock_level


class StockMovement(models.Model):
  MOVEMENT_TYPES = (('IN', 'Stock In (Received)'), ('OUT', 'Stock Out (Used)'))
  material = models.ForeignKey(
      RawMaterial, on_delete=models.CASCADE, related_name='movements'
  )
  movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
  quantity = models.DecimalField(max_digits=10, decimal_places=2)
  supplier = models.ForeignKey(
      Supplier, on_delete=models.SET_NULL, null=True, blank=True
)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  date = models.DateTimeField(auto_now_add=True)
  notes = models.TextField(blank=True, null=True)

  def __str__(self):
    return (
        f'{self.get_movement_type_display()} - {self.quantity}'
        f' {self.material.name}'
)  
class UserProfile(models.Model):
  ROLE_CHOICES = (
      ('admin', 'Admin'),
      ('manager', 'Manager'),
      ('staff', 'Staff'),
  )
  user = models.OneToOneField(
      User, on_delete=models.CASCADE, related_name='profile'
  )
  role = models.CharField(
      max_length=20, choices=ROLE_CHOICES, default='staff'
  )

  def __str__(self):
    return f'{self.user.username} - {self.get_role_display()}'



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    role = 'admin' if instance.is_superuser else 'staff'
    UserProfile.objects.create(user=instance, role=role)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  if hasattr(instance, 'profile'):
    instance.profile.save()
