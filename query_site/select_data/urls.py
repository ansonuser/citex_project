from django.urls import path

from . import views

app_name = 'select_data'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('record/', views.record, name = 'record'),
    path('research_order/', views.research_order, name = 'research_order'),
    path('expect_order/', views.expect_order, name = 'expect_order'),
    path('actual_order/', views.actual_order, name = 'actual_order'),
    path('customer/', views.customer, name = 'customer'),
    path('product/', views.product, name = 'product'),
    path('revise_record/', views.revise_record, name = 'revise_record'),
    path('record_search/', views.record_search, name = 'record_research'),
    path('updateproduct/', views.updateproduct, name = 'updateproduct'),
    path('updatecustomer/', views.updatecustomer, name = 'updatecustomer'),
    path('gettable/', views.gettable, name = 'gettable'),
    path('update_actual_order/', views.update_actual_order, name = 'update_actual_order'),
    path('update_stock_order/', views.update_stock_order, name = 'update_stock_order'),
    path('update_stock_order_detail/', views.update_stock_order_detail, name = 'update_stock_order_detail')
]