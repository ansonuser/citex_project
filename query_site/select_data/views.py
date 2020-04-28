from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .forms import InsertForm
from .models import Product, Customer, Order, Order_detail, Employee, Order_stock, Order_stock_detail, Order_stock_product, Order_detail_po
from .utils import tojson, tojsonframe, custom_table
from django.views.decorators.csrf import csrf_exempt
import re
from django.db.models import Max
import datetime

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
    q = request.POST.dict()
    if q['data'] == "company":
        # name_list = ['company_number', 'company_name', 'site', 'contactor', 'phone','note']
        result_record = Customer.record.recent_records()
        company_record = tojsonframe(result_record, design=[0,1,2])
        return JsonResponse(company_record)
    elif q['data'] =="product":
        # name_list = ['product_number_id', 'product_name']
        result_record = Product.record.recent_records()
        product_record = tojsonframe(result_record)
        return JsonResponse(product_record)
    elif q['data'] =="product_with_stock":
        result_record = Order_stock_product.objects.filter(order_stock_po_id=q['order_stock_po']).values_list("product_number_id") 
        tmp = {}
        for i in result_record:
            tmp[i[0]] = ""
        return JsonResponse(tmp)
    elif q['data'] == 'empolyee':
        result_record = Employee.each_name
        tmp = {}
        for i in result_record:
            tmp[i[0]] = ""
        return  JsonResponse(tmp)
    elif q['data'] =="company_content":
        val = q['val'] 
        c = Customer.objects.get(company_number=val)
        tmp = {}
        for k in ['company_name','site','contactor']:
            tmp[k] = c.serializable_value(k)
        return JsonResponse(tmp)

    elif q['data'] == 'product_content':
        val = q['val']
        p = Product.objects.get(product_number=val)
        tmp = {}
        for k in ["product_name"]:
            tmp[k] = p.serializable_value(k)
        return JsonResponse(tmp)

    elif q['data'] == "ask_no":
        result = tojsonframe(Order.mymanager.get_ask_no())
        return JsonResponse(result)
    elif q['data'] == 'query_actual_order_detail':
        del q['data']
        query_dict = {}
        for k,v in q.items():
            if v != '':
                query_dict[k] = v
          
        for k in ['order_no', 'company_number_id', 'finished', 'deadline', 'expect_date', 'rest_of_date0', 'rest_of_date1']:
            if k not in query_dict:
                query_dict[k] =''
        result_record = Order.mymanager.get_actual_detail(**query_dict)
        # name_list = ['order_no','customer_id','site','contactor','expect_date','deadline','actual_ship_date','invoice_condition','finished','note','note1']
        # result_record = custom_table(result_record, all_name_list = name_list, product_name_list=['product_name','product_amount', 'product_po'])
        # result_record = tojson(result_record, name_list)
        # print(result_record)
        # result = tojsonframe(Order.mymanager.get_actual_detail(** query_dict), keys="index")
        return JsonResponse({'form':result_record})
    elif q['data'] == 'ask_no_content':
        ask_no = q['val']
        result = Order.mymanager.ask_no_content(ask_no)
        tmp = {}
        tmp['company_number_id'] = result[0][0]
        tmp['pay_way'] = result[0][1]
        tmp['deadline'] = result[0][2]
        tmp['product_number_id'] = []
        tmp['product_amount'] = []
        for i in range(len(result)):
            tmp['product_number_id'].append(result[i][3])
            tmp['product_amount'].append(int(result[i][4]))
        return JsonResponse(tmp)
    elif q['data'] == 'ask_no_content_all':
        ask_no = q['val']
        result = Order.mymanager.ask_no_content(ask_no, mode=2)
        tmp = {}
        name_list = ['company_number_id', 'pay_way', 'employee_id', 'note_expect_order','ask_date', 'demand_date', 'deadline']
        tmp['ask_no'] = ask_no
        for idx,name in enumerate(name_list):
            if result[0][idx] is not None:
                val = result[0][idx]
            elif isinstance(result[0][idx], datetime.datetime):
                val = result[0][idx].strftime("%Y/%m/%d")
            else:
                val = ''
            tmp[name] = val
        tmp['product'] = []
        for row in range(len(result)):
            tmp['product'].append({'product_number_id':result[row][-2]})
            tmp['product'][row].update({'product_amount':int(result[row][-1])})
        return JsonResponse(tmp)
    elif q['data'] == 'order_stock_po':
        result_record = Order_stock.objects.values_list("order_stock_po") 
        tmp = {}
        for i in result_record:
            tmp[i[0]] = ""
        return JsonResponse(tmp)
    elif q['data'] == "order_content":
        result = Order.mymanager.get_order_content(q['val'])
        tmp = {}
        tmp['result'] = result
        return JsonResponse(tmp)
    elif q['data'] == "order_no":
        result = tojsonframe(Order.mymanager.get_order_no())
        return JsonResponse(result)
    elif q['data'] == 'product_po':
        result_record = Order.mymanager.get_vailable_product_po(q['val']) 
        tmp = {}
        for i in result_record:
            tmp[i[0]] = ""
        return JsonResponse(tmp)
    elif q['data'] == 'export_order':
        try:
            result = {}
            update_form = q['val']
            each_attribute = update_form.split('&')
            for each in each_attribute:
                splits = each.split('=')
                if splits[1] != '':
                    if splits[0] not in result:
                        result[splits[0]] = [splits[1]]
                    else:
                        result[splits[0]].append(splits[1])
            count = len(result['product_number_id'])     

            keys = [i for i in result.keys() if i not in ['order_no', 'actual_ship_date', 'invoice_condition']]
            current_order_id = Order.objects.get(order_no=result['order_no'][0]).order_all_id
            for i in range(count):
                current_order_detail_id = Order_detail.objects.get(order_id_id= current_order_id , product_number_id=result['product_number_id'][i]).order_detail_id
                update_dict = {'order_detail_id_id':current_order_detail_id}
                for k in keys:
                    update_dict.update({k:result[k][i]})
                odp = Order_detail_po(**update_dict) 
                odp.save()
                Order.mymanager.update_export_stock_detail(**update_dict) #減去庫存
            
            Order.mymanager.update_export_order_status(order_id_id=current_order_id, actual_ship_date=result['actual_ship_date'][0], invoice_condition = result['invoice_condition'][0]) #更新出貨訂單狀態
            return JsonResponse({})
        except:
            raise
    elif q['data'] == 'renew_expect_order':
        name_list = [ "ask_no", "company_number_id",'pay_way','employee_id','ask_date','demand_date', 'deadline',"note"]
        result_record = Order_detail.record.expect_order_records(time_limit=q['limit'])
        result_record = custom_table(result_record, all_name_list = name_list)
        return JsonResponse({'form':result_record})
    elif q['data'] == 'renew_actual_order':
        result_record = Order_detail.record.expect_order_records(time_limit=30, mode=2)
        name_list = ['ask_no','order_no', 'company_number_id', 'get_date', 'expect_date', 'deadline', 'pay_way', 'deliver_way', 'note1']
        result_record = custom_table(result_record, all_name_list = name_list)
        return JsonResponse({'form':result_record})
    elif q['data'] == 'renew_stock_record':
        result = Order_stock_product.mymanager.renew_stock_records(time_limit=q['limit'])
        return JsonResponse({'form':result})
    elif q['data'] == 'renew_stock_record_detail':
        result = Order_stock_product.mymanager.renew_stock_records_detail(time_limit=q['limit'])
        return JsonResponse({'form':result})
    elif q['data'] == 'get_show_stock':
        result = Order_stock_product.mymanager.show_stock(q['t1'],q['t2'])
        return JsonResponse({'form':result})
    elif q['data'] == 'get_invoice_and_stock':
        result = Order_stock_product.mymanager.show_way_actual_invoiceunshipped()
        return JsonResponse({'form':result})
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

@csrf_exempt
def update_actual_order(request):
    put = request.POST
    order_name_list = ['company_number_id', 'get_date', 'expect_date', 'deadline','pay_way', 'order_no', 'deliver_way','invoice_condition', 'note1','ask_no']
    order_detail_name_list = ['product_number_id', 'product_amount']
    update_order = {}
    update_order_detail = {}
    for k in put.keys():
        if k == "note1":
            update_order[k] = put.getlist(k)[0]
        elif k == "invoice_condition":
            update_order['invoice_condition'] = True if put.getlist(k)[0] == 'true' else False
        elif k in order_detail_name_list:
            update_order_detail[k] = put.getlist(k)
        elif k in order_name_list:
            update_order[k] = put.getlist(k)[0]
    if  update_order["ask_no"] != "":
        Order.objects.filter(ask_no=update_order["ask_no"]).update(**update_order)
        current_order_id = Order.objects.get(ask_no=update_order["ask_no"]).order_all_id
    else:
        o = Order(**update_order)
        o.save()
        current_order_id = Order.objects.all().aggregate(Max("order_all_id"))['order_all_id__max']

    if "ask_no" in update_order:
        o = Order_detail.objects.filter(order_id_id=current_order_id)
        o.delete()
    each_dict = {"order_id_id":current_order_id}
    n = len([i for i in update_order_detail["product_number_id"] if i != ""])
    for i in range(n):
        for k in order_detail_name_list:
            each_dict[k] = update_order_detail[k][i]
        o = Order_detail(**each_dict)
        o.save()        
    return HttpResponse("ok")



@csrf_exempt
def update_stock_order(request):
    if request.method=="POST":
        form = request.POST
        update_dict = {}
        n = len([i for i in form.getlist("product_number_id") if i != ''])
        update_dict.update(form.dict())   
        del update_dict['csrfmiddlewaretoken'], update_dict['product_number_id'], update_dict['order_num']
        os = Order_stock(**update_dict)
        os.save()
        po = update_dict["order_stock_po"]
        update_dict = {}
        update_dict["order_stock_po_id"] = po 
        for i in range(n):
            update_dict.update({"order_num":int(form.getlist("order_num")[i])})
            update_dict.update({"product_number_id":form.getlist("product_number_id")[i]})
            osp = Order_stock_product(**update_dict)
            osp.save()
        return JsonResponse({"result":'success'})
    else:
        return JsonResponse({"result":'failed'})


@csrf_exempt
def update_stock_order_detail(request):
    if request.method=="POST":
        form = request.POST
        update_dict = {}
        n = len([i for i in form.getlist("product_number_id") if i != ''])
        update_dict.update(form.dict())   
        del update_dict['csrfmiddlewaretoken'], update_dict['product_number_id'], update_dict['product_num']
        po = update_dict["order_stock_po"]
        for i in range(n):
            update_dict = {}
            current_id = Order_stock_product.objects.get(order_stock_po_id=po, product_number_id = form.getlist("product_number_id")[i]).order_stock_product
            update_dict["order_stock_product_id"] = current_id
            for k in ["product_po", "valid_date", "product_num", "note"]:
                update_dict.update({k:form.getlist(k)[i]})
            osd = Order_stock_detail(**update_dict)
            osd.save()
        Order_stock_product.mymanager.update_stock_order_status(order_stock_po=po)
        return JsonResponse({"result":'success'})
    else:
        return JsonResponse({"result":'failed'})
 
def index(request):
    return render(request,'select_data/index.html')

def expect_order(request):
    name_list = [ "ask_no", "company_number_id",'pay_way','employee_id','ask_date','demand_date', 'deadline',"note"]
    product_list = ['product_number_id','product_amount']
    if request.method == 'POST':
        result = request.POST
        base_dict = {}
        product_dict = {}
        for k in result.keys():
            if k in name_list and result.getlist(k)[0] != "":
                if k == "company_number_id":
                    base_dict[k] = result.getlist(k)[0] 
                elif k == "employee_id":
                    base_dict[k] = int(result.getlist(k)[0].split('-')[-1])
                else:
                    base_dict[k] = result.getlist(k)[0]
            elif k in product_list: 
                product_dict[k] = [j for j in result.getlist(k) if j != ""]
        o = Order(**base_dict)
        o.save()
        current_pk = Order.objects.all().aggregate(Max("order_all_id"))['order_all_id__max']
        for i in range(len(product_dict[product_list[0]])):
            tmp = {"order_id_id":int(current_pk)}
            for k in product_list:
                tmp[k] = product_dict[k][i]
            od = Order_detail(**tmp)
            od.save()
    return render(request,'select_data/expect_order.html')

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

def research_order(request):
    return render(request,'select_data/research_order.html')#, {"formset":result})






