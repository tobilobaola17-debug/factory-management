from django.urls import path
from . import views
from django.contrib import admin
from .views import add_supplier_view, delete_supplier_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/', views.custom_login_view, name='login'
    ),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('products/', views.products_view, name='products'),
    path(
        'update-stock/<int:pk>/',
        views.update_stock_view,
        name='update_stock',
    ), 
    path(
        'add-material/',
        views.add_raw_material_view,
        name='add_raw_material',


    ),
    path(
    'stock-movement/<int:pk>/',
    views.stock_movement_view,
    name='stock_movement',
),

    path('production/', views.production_list_view, name='production_list'),
    path(
    'production/add/',
    views.add_production_run_view,
    name='add_production_run',
),
path('products/add/', views.add_product_view, name='add_product'),
path('suppliers/', views.supplier_list_view, name='supplier_list'),
path('suppliers/add/', views.add_supplier_view, name='add_supplier'),
path('orders/', views.order_list_view, name='order_list'),
path('orders/add/', views.add_order_view, name='add_order'),
path('orders/<int:pk>/dispatch/', views.dispatch_order_view, name='dispatch_order'),
path('materials/', views.raw_material_list_view, name='raw_material_list'),
    path(
        'materials/<int:pk>/movement/',
        views.record_stock_movement_view,
        name='record_stock_movement',
    ),
path('suppliers/add/', add_supplier_view, name='add_supplier'),
path('suppliers/delete/<int:supplier_id>/', delete_supplier_view, name='delete_supplier'),
]    

