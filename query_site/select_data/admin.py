from django.contrib import admin
from .models import Product, Customer, Order_stock, Order_stock_detail, Employee, Order, Order_detail

# Register your models here.
admin.site.register( Product)
admin.site.register(Customer)
admin.site.register(Order_stock)
admin.site.register(Order_stock_detail)
admin.site.register(Employee)
admin.site.register(Order)
admin.site.register(Order_detail)
