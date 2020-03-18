from django.contrib import admin
from .models import Company, Factory, People, Product, Stock, Employee, Order_detail, Order_get

# Register your models here.
admin.site.register(Company)
admin.site.register(Factory)
admin.site.register(People)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Employee)
admin.site.register(Order_get)
admin.site.register(Order_detail)
