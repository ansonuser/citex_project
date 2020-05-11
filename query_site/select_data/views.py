from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,Http404
from django.template import loader
from .forms import InsertForm
from .models import Product, Customer, Order, Order_detail, Employee, Order_stock, Order_stock_detail, Order_stock_product, Order_detail_po
from .utils import tojson, tojsonframe, custom_table
from django.views.decorators.csrf import csrf_exempt
import re
from django.db.models import Max
import datetime
import logging

now = datetime.date.today()
logging.basicConfig(filename="%s.log"%(str(now)), format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M %p' , level=logging.INFO, filemode='a+')
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
                if k != 'finished':
                    query_dict[k] = v
                else:
                    query_dict[k] = '1' if k == 'true' else '0'
          
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
    elif q['data'] == 'order_no_content_all':
        order_no = q['val']
        result = Order.mymanager.order_no_content(order_no)
        tmp = {}
        name_list = ['company_number_id', 'get_date', 'expect_date', 'deadline', 'pay_way', 'deliver_way', 'invoice_condition', 'note1']
        tmp['order_no'] = order_no
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
    elif q['data'] == 'stock_content':
        stock_po = q['val']
        result = Order_stock_product.mymanager.stock_content(stock_po)
        tmp = {}
        name_list = ['order_stock_date', 'note']
        tmp['order_stock_po'] = stock_po
        for idx, name in enumerate(name_list):
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
    elif q['data'] == 'stock_content_detail':
        stock_po = q['val']
        result = Order_stock_product.mymanager.stock_content_detail(stock_po)
        tmp = {}
        tmp['order_stock_po'] = stock_po
        tmp['product'] = []
        for i in range(len(result)):
            tmp['product'].append({})
            for idx,k in enumerate(['product_number_id', 'product_po', 'valid_date', 'product_num', 'note']):
                if result[i][idx] is not None:
                    val = result[i][idx]
                elif isinstance(result[i][idx], datetime.datetime):
                    val = result[i][idx].strftime("%Y/%m/%d")
                else:
                    val = ''
                tmp['product'][i].update({k:val})
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
    elif q['data'] == 'export_order': #出貨
        user = request['user']
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
            logging.warning('%s export product and update status of %s' %(user, result['order_no'][0]))
            return JsonResponse({})
        except:
            logging.warning('Export product fail while %s use' %(user))
            raise
    elif q['data'] == 'renew_expect_order':
        result_record = Order_detail.record.expect_order_records(time_limit=q['limit'])
        return JsonResponse({'form':result_record})
    elif q['data'] == 'renew_actual_order':
        result_record = Order_detail.record.expect_order_records(time_limit=30, mode=2)
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

################## update api
########################################################################
@csrf_exempt
def updatecustomer(request):
    user = request['user']
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
    logging.info("%s update customer id: %s" %(user, c.company_number))            
    return HttpResponse("ok")


@csrf_exempt
def update_actual_order(request):
    user = request.session['user']
    if request.method == "POST":
        respond = request.POST
        form = {}
        mode = 0
        for k in respond.keys():
            if k != 'csrfmiddlewaretoken':
                if k != 'mode':
                    list_or_not = len(respond.getlist(k))
                    if list_or_not != 1:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)
                    else:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)[0]
                else:
                    mode = int(respond.getlist('mode')[0])
        update_dict = {}
        order_detail_name_list = ['product_number_id', 'product_amount']
        order_no = form['order_no']
        update_dict.update(**form)
        n = len([i for i in form["product_number_id"] if i != ''])
        if mode > 0:
            o = Order.objects.get(order_no=order_no)
            Order_detail.objects.filter(order_id_id=o.order_all_id).delete()
            o.delete()
        if mode != 1:
            for k in order_detail_name_list:
                del update_dict[k]
            update_dict['invoice_condition'] = True if update_dict['invoice_condition'] == 'true' else False
            if  (mode == 0):
                if (update_dict["ask_no"] != ""):
                    Order.objects.filter(ask_no=update_dict["ask_no"]).update(**update_dict)
                    current_order_id = Order.objects.get(ask_no=update_dict["ask_no"]).order_all_id
            else:
                o = Order(**update_dict)
                o.save()
                current_order_id = Order.objects.all().aggregate(Max("order_all_id"))['order_all_id__max']
            if (mode == 0) & ("ask_no" in update_dict):
                o = Order_detail.objects.filter(order_id_id=current_order_id)
                o.delete()
            each_dict = {"order_id_id":current_order_id}
            for i in range(n):
                for k in order_detail_name_list:
                    each_dict[k] = form[k][i]
                o = Order_detail(**each_dict)
                o.save() 
            logging.info('%s updated actual order with order_no:%s' %(user, order_no))       
        return JsonResponse({"result":'success'})
    else:
        # logging.warning('%s failed to update actual order with order_no:%s' %(user, order_no))
        return JsonResponse({"result":'failed'})

@csrf_exempt
def update_stock_order(request):
    user = request.session['user']
    if request.method=="POST":
        respond = request.POST
        form = {}
        mode = 0 # 1 update, 2 delete
        for k in respond.keys():
            if k != 'csrfmiddlewaretoken':
                if k != 'mode':
                    list_or_not = len(respond.getlist(k))
                    if list_or_not != 1:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)
                    else:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)[0]
                else:
                    mode = int(respond.getlist('mode')[0])
        if (mode > 0):
            Order_stock.objects.filter(order_stock_po = form["order_stock_po"]).delete() 
            Order_stock_product.objects.filter(order_stock_po_id= form["order_stock_po"]).delete() 
            logging.info('%s deleted stock order with order_stock_po:%s' %(user, form['order_stock_po'])) 
        if (mode != 1):
            update_dict = {}
            n = len([i for i in form["product_number_id"] if i != ''])
            update_dict.update(form)   
            del update_dict['product_number_id'], update_dict['order_num']
            os = Order_stock(**update_dict)
            os.save()
            po = update_dict["order_stock_po"]
            update_dict = {}
            update_dict["order_stock_po_id"] = po 
            for i in range(n):
                update_dict.update({"order_num":int(form["order_num"][i])})
                update_dict.update({"product_number_id":form["product_number_id"][i]})
                osp = Order_stock_product(**update_dict)
                osp.save()
            logging.info('%s inserted stock order with order_stock_po:%s' %(user, po))  
        return JsonResponse({"result":'success'})
    else:
        return JsonResponse({"result":'failed'})


@csrf_exempt
def update_stock_order_detail(request):
    user = request.session['user']
    if request.method=="POST":
        form = {}
        mode = 0
        respond = request.POST
        for k in respond.keys():
            if k != 'csrfmiddlewaretoken':
                if k != 'mode':
                    list_or_not = len(respond.getlist(k))
                    if list_or_not != 1:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)
                    else:
                        form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)[0]
                else:
                    mode = int(respond.getlist('mode')[0])
        update_dict = {}
        n = len([i for i in form["product_number_id"] if i != ''])
        po = form["order_stock_po"]
        if mode > 0:
            for i in range(n):
                current_id = Order_stock_product.objects.get(order_stock_po_id=po, product_number_id = form["product_number_id"][i]).order_stock_product
                Order_stock_detail.objects.filter( order_stock_product_id = current_id).delete()
            Order_stock.objects.filter(order_stock_po=po).update(order_stock_status='0')
            logging.info('%s deleted stock order detail with order_stock_po:%s' %(user, po))  
        if mode != 1:
            update_dict.update(form)   
            del update_dict['product_number_id'], update_dict['product_num']
            for i in range(n):
                update_dict = {}
                current_id = Order_stock_product.objects.get(order_stock_po_id=po, product_number_id = form["product_number_id"][i]).order_stock_product
                update_dict["order_stock_product_id"] = current_id
                for k in ["product_po", "valid_date", "product_num", "note"]:
                    update_dict.update({k:form[k][i]}) 
                osd = Order_stock_detail(**update_dict)
                osd.save()
            Order_stock_product.mymanager.update_stock_order_status(order_stock_po=po)
            logging.info('%s inserted stock order detail with order_stock_po:%s' %(user, po))  
        return JsonResponse({"result":'success'})
    else:
        return JsonResponse({"result":'failed'})
 

@csrf_exempt
def update_expect_order(request):
    user = request.session['user']
    if request.method == 'POST':
        respond = request.POST
        product_list = ['product_number_id','product_amount']
        form = {}
        mode = 0
        for k in respond.keys():
            if k != 'csrfmiddlewaretoken':
                if k != 'mode':
                    list_or_not = len(respond.getlist(k))
                    if k == "employee_id":
                        form[k] = respond.getlist(k)[0].split('-')[1]
                    else:
                        if list_or_not != 1:
                            form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)
                        else:
                            form[re.sub(r'[\[\]]','',k)] = respond.getlist(k)[0]
                else:
                    mode = int(respond.getlist('mode')[0])

        update_dict = {}
        n = len([i for i in form["product_number_id"] if i != ''])
        ask_no= form["ask_no"]
        if mode > 0:
            o = Order.objects.filter(ask_no=ask_no)
            order_all_id = o.order_all_id
            o.delete()
            o = Order_detail.objects.filter(order_id_id=order_all_id)
            n = len(o)
            for i in range(n):
                Order_detail_po.objects.filter(order_detail_id_id = o[i].order_detail_id).delete()
            o.delete()
            logging.info('%s deleted expect order with ask_noo:%s' %(user, ask_no))  
        if mode != 1:
            update_dict.update(form)
            for k in product_list:
                del update_dict[k]
            o = Order(**update_dict)
            o.save()
            current_pk = Order.objects.all().aggregate(Max("order_all_id"))['order_all_id__max']
            product_dict = {}
            product_dict["order_id_id"] = current_pk
            for i in range(n):
                for k in product_list:
                    product_dict.update({k:form[k][i]})
                od = Order_detail(**product_dict)
                od.save() 
            logging.info('%s inserted expect order with ask_noo:%s' %(user, ask_no))  
        return JsonResponse({"result":'success'})
    else:
        return JsonResponse({"result":'failed'})  



@csrf_exempt
def login(request):
    request.session['login'] = ''
    if request.method=='POST':
        respond = request.POST.dict()
        mode, usr, pwd = respond['mode'], respond['usr'], respond['pwd']
        usr = usr.split('-')
        name, pid = usr[0], usr[1]
        e = Employee.objects.filter(employee_name=name, employee_id=pid)
        if str(mode) == '0':   
            if e[0].password is None:
                e.update(password=pwd)
            else:
                return JsonResponse({'result':'failed'})
        else:
            if e[0].password != pwd:
                return JsonResponse({'result':'failed'})
            else:
                request.session['login'] = 'true'
                request.session['user'] = usr
        return JsonResponse({'result':'success'})
    else:
        return JsonResponse({'result':'failed'})
#####################################################################
def index(request):
    keys = [k for k in request.session.keys()]
    for key in keys:
        del request.session[key]
    return render(request,'select_data/index.html')

def customer(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
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
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')
def product(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
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
        else:
            return render(request,'select_data/index.html') 
    else:
        return render(request,'select_data/index.html')
  
def record(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/record.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')  

def revise_record(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/revise_record.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')
def record_search(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/record_search.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')
def research_order(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/research_order.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')
def actual_order(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/actual_order.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')
def expect_order(request):
    if 'login' in request.session:
        if request.session['login'] == 'true':
            return render(request,'select_data/expect_order.html')
        else:
            return render(request,'select_data/index.html')
    else:
        return render(request,'select_data/index.html')


