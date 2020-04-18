from django.db import models
import re
from django.forms import ModelForm


##### define manager (for display purpose)


class ProductManager(models.Manager):
    def recent_records(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT product_number, product_name FROM select_data_product p ORDER BY p.product_number 
                """
            )
            respond = cursor.fetchall()
        return respond

class CustomerManager(models.Manager):
    def recent_records(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT company_number, company_name, site, contactor, phone, note FROM select_data_customer c 
                """
            )
            respond = cursor.fetchall()
        return respond

class OrderManager(models.Manager):
    def expect_order_records(self):
        from django.db import connection
        # [ "company_number_id","ask_no","note",'pay_way','charger','ask_date','demand_date', 'deadline']
        # ['product_name','product_amount']
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT company_number_id, ask_no, pay_way, e.employee_name, ask_date, demand_date, deadline, od.product_number_id, 
                od.product_amount, note, last_modified FROM select_data_order o, select_data_employee e, select_data_order_detail od
                WHERE o.employee_id = e.employee_id AND o.order_all_id = od.order_id_id ORDER BY o.last_modified 
                """
            )
            respond = cursor.fetchall()
        return respond

    def ask_no_content(self, ask_no):
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT company_number_id, pay_way, deadline, od.product_number_id, 
                od.product_amount FROM select_data_order o, select_data_order_detail od
                WHERE o.order_all_id = od.order_id_id AND o.ask_no =:ask_no """, ({'ask_no':ask_no}))
            respond = cursor.fetchall()
        return respond


    def recent_records(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT company_number, company_name, site, contactor, phone, note FROM select_data_customer 
                """
            )
            respond = cursor.fetchall()
        return respond

    def select_employee(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT employee_name ||'-' || cast(employee_id as text) FROM select_data_employee; 
                """
            )
            respond = cursor.fetchall()

        return respond
    def get_ask_no(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT ask_no FROM select_data_order; 
                """
            )
            respond = cursor.fetchall()

        return respond
    def get_actual_detail(self, **kwargs):
        from django.db import connection
        with connection.cursor() as cursor:
            command =  """
                SELECT o.order_no, o.company_number_id, cust.contactor, cust.site, p.product_name, od.product_amount, o.expect_date, o.deadline, o.finished,
                o.actual_ship_date, od.product_po, o.invoice_condition, o.note, o.note1 FROM select_data_order o, select_data_order_detail od, select_data_customer cust,
                select_data_product p WHERE o.order_all_id = od.order_id_id AND o.company_number_id = cust.company_number AND od.product_number_id = p.product_number 
                """ + " AND o.order_no =:order_no"*(kwargs['order_no'] != '') + " AND o.company_number_id =:company_number_id "*(kwargs['company_number_id'] != '') + " AND o.finished =:finished"*(kwargs['finished'] != '') +\
                    " AND o.deadline =:deadline "*(kwargs['deadline'] != '') + " AND o.expect_data =:expect_date "*(kwargs['expect_date'] != '') + " AND ((julianday('now') - julianday(o.deadline)) >=:rest_of_date0) AND (julianday('now') - julianday(o.deadline)) <:rest_of_date1"*(kwargs['rest_of_date0'] != '')
            # print(command)
            cursor.execute(
               command, (kwargs )
            )
            respond = cursor.fetchall()

        return respond
class InsertManager(models.Manager):
    def recent_records(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.company_name, f.factory_site, ple.people_name, duct.product_name, og.po_num, od.product_num,
                        og.get_order_date, od.expected_ship_date, od.other_command, od.last_modified 
                FROM select_data_company c, select_data_factory f, select_data_people ple,  select_data_product duct, select_data_order_get og, select_data_order_detail od
                WHERE og.order_id = od.order_id_id and duct.product_id = od.product_id_id and ple.people_id = od.custom_id_id and f.factory_id = ple.factory_id_id and
                c.company_id = f.company_id_id 
                ORDER BY od.last_modified  DESC
                LIMIT 10
                """
            )
            respond = cursor.fetchall()
        return respond

class StockManager(models.Manager):
    def recent_records(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT duct.product_name, stock.produced_date, stock.num_rest, CAST((julianday('now') -  julianday(stock.produced_date)) AS Integer) 
                FROM  select_data_product duct, select_data_stock stock
                WHERE  duct.product_id = stock.product_id_id 
                ORDER BY stock.produced_date  DESC
                """
            )
            respond = cursor.fetchall()
        return respond


##### define table


# product table
class Product(models.Model):
    """
    pk: product_name
    """    
    product_number = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=50)
    objects = models.Manager()
    record = ProductManager()
    def __str__(self):
        return '商品編號:'+ self.product_number  + ', 名稱:' + str(self.product_name)

# company table
class Customer(models.Model):
    """
    record the customer name
    pk: customer number
    """
    company_number = models.CharField(max_length=50, primary_key=True)
    company_name = models.CharField(max_length=50)
    site = models.CharField(max_length=50)
    contactor = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    note = models.CharField(max_length=100, null=True)
    objects = models.Manager()
    record = CustomerManager()
    def __str__(self):
        return "公司:"+ self.company_name + ", 聯絡人:"+self.contactor

# order source
class Order_stock(models.Model):
    """
    pk: order stock po
    """
    
    order_stock_date = models.DateField()
    order_stock_po = models.CharField(max_length=50, primary_key=True)
    order_stock_status = models.IntegerField(default=0) # 0:下單 1:運送中 2:即將到貨 3:已到達 4:部分到貨
    note = models.CharField(max_length=50, null=True)
    objects = models.Manager()
    def __str__(self):
        return "訂貨編號:"+ self.order_stock_po + ", 狀態:"+ str(self.order_stock_status)

class Order_stock_product(models.Model):
    order_stock_product = models.AutoField(primary_key=True)
    order_stock_po = models.ForeignKey(Order_stock, on_delete=models.CASCADE)
    product_number = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_num = models.IntegerField()
    objects = models.Manager()
    def __str__(self):
        return "訂貨編號:"+ self.order_stock_po + ", 商品" + self.product_number
# order source detail
class Order_stock_detail(models.Model):
    """
    pk: order stock detail
    """
    order_stock_detail_id = models.AutoField(primary_key=True)
    order_stock_po = models.ForeignKey(Order_stock, on_delete=models.CASCADE)
    product_number = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_po = models.CharField(max_length=50)
    valid_date = models.DateField()
    product_num = models.IntegerField()
    note = models.CharField(max_length=50, null=True)
    order_detail_status = models.BooleanField(default=False)
    objects = models.Manager()
    def __str__(self):
        return "商品批號:" + self.product_po + ", 品名:" + self.product_number + ", 數量" + str(self.product_num) 

# company employee
class Employee(models.Model):
    """
    pk: empolyee id
    """
    employee_id = models.AutoField(primary_key=True)
    employee_name = models.CharField(max_length=50)
    employee_position  = models.CharField(max_length=50)
    employee_state = models.CharField(max_length=10)
    start_time = models.DateField()
    each_name = OrderManager().select_employee()
    objects = models.Manager()
    def __str__(self):
        return "員工名稱:"+ self.employee_name

# order b2b
class Order(models.Model):
    """
    record order b2b
    pk: order_id
    """
    order_all_id = models.AutoField(primary_key=True)
    company_number = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ask_no = models.CharField(max_length=50, null=True)
    pay_way = models.CharField(max_length=50, null=True)
    note = models.CharField(max_length=50, null=True)
    ask_date = models.DateField(null=True)
    demand_date = models.DateField(null=True)
    deadline = models.DateField(null=True)
    get_date = models.DateField(null=True)
    expect_date = models.DateField(null=True)
    order_no = models.CharField(max_length=50, null=True)
    deliver_way = models.CharField(max_length=50, null=True)
    note1 = models.CharField(max_length=50, null=True)
    invoice_condition = models.BooleanField(default=False)
    actual_ship_date = models.DateField(null=True)
    finished = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null=True)
    last_modified = models.DateField(auto_now=True)
    objects = models.Manager()
    mymanager = OrderManager()

    def __str__(self):
        return "流水編號:" +  self.order_all_id + ",訂單狀態:"  + "完成" if self.finished else "未完成"

class Order_detail(models.Model):
    """
    detail for order
    """
    order_detail_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_number = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_po = models.CharField(max_length=50, null=50)
    product_amount = models.IntegerField()
    objects = models.Manager()
    record = OrderManager()
    def __str__(self):
        return "流水編號:" + self.order_id + "," + self.product_number + ":" + self.product_amount

###### define form
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name']
class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_name', 'employee_position', 'employee_state', 'start_time']


