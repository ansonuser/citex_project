from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .forms import InsertForm
from .models import Product, Customer, Order, Order_detail
from .utils import tojson, tojsonframe
from django.views.decorators.csrf import csrf_exempt
import re
from django.db.models import Max


@csrf_exempt
def updateproduct(request):
    put = request.POST
    for k in put.keys():
        v = put.getlist(k)
        update_pattern = re.compile("update_row.*")
        delete_pattern = re.compile("delete_row.*")
        if update_pattern.match(k) is not None:
            p = Product.objects.get(product_number=v[0])
            if p.product_name != v[1]:
                p.product_name = v[1]
                p.save()
        elif delete_pattern.match(k) is not None:
            p = Product.objects.filter(product_number=v[0])
            p.delete()                
    return HttpResponse("ok")

@csrf_exempt
def gettable(request):
    data = request.POST['data']
    if data == "company":
        name_list = ['company_number', 'company_name', 'site', 'contactor', 'phone','note']
        result_record = Customer.record.recent_records()
        company_record = tojsonframe(result_record, name_list, design=[0,1,2])
        return JsonResponse(company_record)
    elif data =="product":
        name_list = ['product_number', 'product_name']
        result_record = Product.record.recent_records()
        product_record = tojsonframe(result_record, name_list)
        return JsonResponse(product_record)

    elif data == "order_from_customer":
        return JsonResponse({})
    elif data == "order":
        return JsonResponse({})

@csrf_exempt
def updatecustomer(request):
    put = request.POST
    name_list = ['company_name', 'site', 'contactor', 'phone','note']
    for k in put.keys():
        v = put.getlist(k)
        update_pattern = re.compile("update_row.*")
        delete_pattern = re.compile("delete_row.*")
        if update_pattern.match(k) is not None:
            c = Customer.objects.filter(company_number=v[0]).update(**{k:v for k,v in zip(name_list,v[1:])})
        elif delete_pattern.match(k) is not None:
            c = Customer.objects.filter(company_number=v[0])
            c.delete()                
    return HttpResponse("ok")


# @csrf_exempt
# def updateorder(request):
#     put = request.POST
#     name_list = ['custom_no', 'ask_no', 'pay_way', 'writer','note', 'ask_date',]
#     for k in put.keys():
#         v = put.getlist(k)
#         update_pattern = re.compile("update_row.*")
#         delete_pattern = re.compile("delete_row.*")
#         if update_pattern.match(k) is not None:
#             c = Customer.objects.filter(company_number=v[0]).update(**{k:v for k,v in zip(name_list,v[1:])})
#         elif delete_pattern.match(k) is not None:
#             c = Customer.objects.filter(company_number=v[0])
#             c.delete()                
#     return HttpResponse("ok")    


def index(request):
    return render(request,'select_data/index.html')

def expect_order(request):
    result_record = Order_detail.record.expect_order_records()
    name_list = [ "customer_id","ask_no","note",'pay_way','charger','ask_date','demand_date', 'deadline']
    product_list = ['product_name','product_amount']
    result_record = tojsonframe(result_record, name_list+product_list)

    if request.method == 'POST':
        result = request.POST
        base_dict = {}
        product_dict = {}
        for k in result.keys():
            if k in name_list:
                base_dict[k] = result.getlist(k)
            elif k in product_list: 
                product_dict[k] = result.getlist(k)[:-1]
        
        o = Order(**base_dict)
        o.save()
        current_pk = Order.objects.all().aggregate(Max("order_all_id"))
        for i in range(len(product_dict[product_list[0]])):
            tmp = {"order_id":current_pk}
            for k in product_list:
                tmp[k] = product_dict[k][i]
            od = Order_detail(**tmp)
            od.save()
            
    return render(request,'select_data/expect_order.html',{"formset":result_record})

def actual_order(request):
    return render(request,'select_data/actual_order.html')

def customer(request):
    name_list = ['company_number', 'company_name', 'site', 'contactor', 'phone','note']
    result_record = Customer.record.recent_records()
    result_record = tojson(result_record, name_list)
    if request.method == 'POST':
        result = request.POST
        result = result.dict()
        new_number = result["company_number"]
        all_number = [i['company_number'] for i in result_record]
        if new_number in all_number:
            return render(request, 'select_data/customer.html', {"duplicate":True,"formset":result_record})
        else:
            del result['csrfmiddlewaretoken']
            c = Customer(**result)
            c.save()
            result_record = tojson(Customer.record.recent_records(), name_list)
            return render(request, 'select_data/customer.html',{"duplicate":False,"formset":result_record} )
    return render(request,'select_data/customer.html', {"duplicate":"Empty","formset":result_record})


def product(request):
    name_list = ['product_number', 'product_name']
    result_record = Product.record.recent_records()
    result_record = tojson(result_record, name_list)
    if request.method == 'POST':
        result = request.POST
        new_id = result["product_id"]
        new_name = result["product_name"]
        all_name = [ i['product_name'] for i in result_record]
        all_id = [ i['product_number'] for i in result_record]
        if new_id in all_id or new_name in all_name:
            return render(request,'select_data/product.html',{"duplicate":True,"formset":result_record})
        else:
            p =  Product(product_number=new_id , product_name=new_name)
            p.save()
            result_record = Product.record.recent_records()
            result_record = tojson(result_record, name_list)
            return render(request,'select_data/product.html',{"duplicate":False,"formset":result_record})
    return render(request,'select_data/product.html',{"duplicate":"Empty","formset":result_record})
  

def record(request):
    # result = Stock.record.recent_records()
    # if request.method == 'POST':
    #     q = request.POST
    #     # input table    
    #     insert_form = InsertForm(q)
    #     # check if exist
    #     ## company

    #     # display record
    #     result = Order_detail.record.recent_records()
    #     if insert_form.is_valid():
    #         pass  
    # return render(request,'select_data/insert.html', {"formset":result})
    return render(request,'select_data/record.html')#, {"formset":result})

def revise_record(request):
    return render(request,'select_data/revise_record.html')



def record_search(request):
    return render(request,'select_data/record_search.html')

def insert(request):
    # result = Order_detail.record.recent_records()
    # if request.method == 'POST':
    #     q = request.POST
    #     # input table    
    #     insert_form = InsertForm(q)
    #     conn = make_connection(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #     # command =  f"""SELECT company_name FROM select_data_company
    #     #         """
    #     # print(insert_form.__dict__)
    #     # cursor = conn.cursor()
    #     # cursor.execute(command)
    #     # _ = cursor.fetchall()
    #     # one = cursor.fetchone()
    #     # print(one)
    #     # a = [i[0] for i in _]
    #     # if 'TSMC' in a:
    #     #     print("pass1")
    #     # print(a)
    #     # print(a[0] == 3)
    #     # print(a[0][0] == 'TSMC')
        
    #     current_id_dict = utils_insert_single(conn, insert_form)
        
    #     succeed = utils_insert_relation(conn, insert_form, current_id_dict)
    #     conn.close()
    #     # if succeed:
    #     #     print("update database")
    #     # else:
    #     #     print("[Error] Fail to update database")
    #     # display record
    #     result = Order_detail.record.recent_records()
    #     if insert_form.is_valid():
    #         pass  

    return render(request,'select_data/insert.html')#, {"formset":result})


def select(request):
    return render(request,'select_data/select.html')



