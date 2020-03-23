from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import InsertForm
from .models import *
from .utils import *





def index(request):
    return render(request,'select_data/index.html')

def expect_order(request):
    return render(request,'select_data/expect_order.html')


def record(request):
    result = Stock.record.recent_records()
    if request.method == 'POST':
        q = request.POST
        # input table    
        insert_form = InsertForm(q)
        # check if exist
        ## company

        # display record
        result = Order_detail.record.recent_records()
        if insert_form.is_valid():
            pass  
    # return render(request,'select_data/insert.html', {"formset":result})
    return render(request,'select_data/record.html', {"formset":result})


def insert(request):
    result = Order_detail.record.recent_records()
    if request.method == 'POST':
        q = request.POST
        # input table    
        insert_form = InsertForm(q)
        conn = make_connection(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # command =  f"""SELECT company_name FROM select_data_company
        #         """
        # print(insert_form.__dict__)
        # cursor = conn.cursor()
        # cursor.execute(command)
        # _ = cursor.fetchall()
        # one = cursor.fetchone()
        # print(one)
        # a = [i[0] for i in _]
        # if 'TSMC' in a:
        #     print("pass1")
        # print(a)
        # print(a[0] == 3)
        # print(a[0][0] == 'TSMC')
        
        current_id_dict = utils_insert_single(conn, insert_form)
        
        succeed = utils_insert_relation(conn, insert_form, current_id_dict)
        conn.close()
        # if succeed:
        #     print("update database")
        # else:
        #     print("[Error] Fail to update database")
        # display record
        result = Order_detail.record.recent_records()
        if insert_form.is_valid():
            pass  

    return render(request,'select_data/insert.html', {"formset":result})


def select(request):
    return render(request,'select_data/select.html')



