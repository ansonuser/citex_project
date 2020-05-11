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
    def expect_order_records(self, time_limit, mode = 1):
        from django.db import connection
        respond = {}
        if mode == 1:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT DISTINCT ask_no, company_number_id, pay_way, e.employee_name, ask_date, demand_date, deadline, note, p.product_name, od.product_amount
                    FROM 
                    select_data_order o, select_data_employee e, select_data_order_detail od, select_data_product p
                    WHERE 
                    o.employee_id = e.employee_id 
                    AND 
                    o.order_all_id = od.order_id_id  
                    AND
                    od.product_number_id = p.product_number
                    AND
                    ((julianday('now') - julianday(o.last_modified)) <= :time_limit) ORDER BY o.order_all_id
                    """,({'time_limit':time_limit}))
                return cursor.fetchall()
            #     respond.update({'ask_no_info':cursor.fetchall()})
            # with connection.cursor() as cursor:
            #     cursor.execute(
            #         """
            #         SELECT od.order_id_id, p.product_name, od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_product p
            #         WHERE o.order_all_id = od.order_id_id  
            #         AND
            #         od.product_number_id = p.product_number
            #         AND 
            #         ((julianday('now') - julianday(o.last_modified)) <= :time_limit) ORDER BY o.order_all_id
            #         """,({'time_limit':time_limit}))
            #     respond.update({'ask_no_product_info':cursor.fetchall()})

        elif mode == 2:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT DISTINCT o.order_no, o.ask_no, company_number_id, get_date, expect_date, deadline, pay_way, deliver_way, note1, p.product_name, od.product_amount
                    FROM select_data_order o, select_data_order_detail od, select_data_product p
                    WHERE  
                    o.order_all_id = od.order_id_id
                    AND
                    p.product_number = od.product_number_id
                    AND
                    o.order_no IS NOT NULL
                    AND
                    ((julianday('now') - julianday(o.last_modified)) <= :time_limit) ORDER BY o.order_all_id
                    """,({'time_limit':time_limit}))

                return cursor.fetchall()
            #     respond.update({'order_no_info':cursor.fetchall()})
            # with connection.cursor() as cursor:
            #     cursor.execute(
            #         """
            #         SELECT od.order_id_id,  od.product_number_id, od.product_amount FROM select_data_order o, select_data_order_detail od
            #         WHERE o.order_all_id = od.order_id_id  AND ((julianday('now') - julianday(o.last_modified)) <= :time_limit) ORDER BY o.order_all_id
            #         """,({'time_limit':time_limit}))
            #     respond.update({'order_no_product_info':cursor.fetchall()})            
        return respond

    def ask_no_content(self, ask_no, mode = 1):
        """
        mode: 1, draw for actual order
              2, for modification of expect order
        """
        from django.db import connection
        with connection.cursor() as cursor:
            if mode == 1:
                cursor.execute(
                    """
                    SELECT company_number_id, pay_way, deadline, od.product_number_id, 
                    od.product_amount FROM select_data_order o, select_data_order_detail od
                    WHERE o.order_all_id = od.order_id_id AND o.ask_no =:ask_no """, ({'ask_no':ask_no}))
            elif mode == 2:
                cursor.execute(
                    """
                    SELECT company_number_id, pay_way, e.employee_name ||'-' || cast(e.employee_id as text), note, ask_date, demand_date, deadline, od.product_number_id, 
                    od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_employee e
                    WHERE o.order_all_id = od.order_id_id AND o.employee_id = e.employee_id AND o.ask_no =:ask_no """, ({'ask_no':ask_no}))
            elif mode == 3:
                cursor.execute(
                    """
                    SELECT o.ask_no, o.order_no, company_number_id, get_date, expect_date, deadline, pay_way, deliver_way, note1, deadline, od.product_number_id, 
                    od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_employee e
                    WHERE o.order_all_id = od.order_id_id AND o.employee_id = e.employee_id AND o.ask_no =:ask_no """, ({'ask_no':ask_no}))
            respond = cursor.fetchall()
        return respond
    def order_no_content(self, order_no, mode = 1):
        """
        mode: 1, for modification of actual order
        """
        from django.db import connection
        with connection.cursor() as cursor:
            if mode == 1:
                cursor.execute(
                    """
                    SELECT company_number_id, get_date, expect_date, deadline, 
                    pay_way, deliver_way, invoice_condition, o.note1, od.product_number_id, od.product_amount 
                    FROM 
                    select_data_order o, select_data_order_detail od
                    WHERE 
                    o.order_all_id = od.order_id_id 
                    AND 
                    o.order_no = :order_no 
                    """, ({'order_no':order_no}))
                return cursor.fetchall()
            # elif mode == 2:
            #     cursor.execute(
            #         """
            #         SELECT company_number_id, pay_way, e.employee_name ||'-' || cast(e.employee_id as text), note, ask_date, demand_date, deadline, od.product_number_id, 
            #         od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_employee e
            #         WHERE o.order_all_id = od.order_id_id AND o.employee_id = e.employee_id AND o.ask_no =:ask_no """, ({'order_no':order_no}))
            # elif mode == 3:
            #     cursor.execute(
            #         """
            #         SELECT o.ask_no, o.order_no, company_number_id, get_date, expect_date, deadline, pay_way, deliver_way, note1, deadline, od.product_number_id, 
            #         od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_employee e
            #         WHERE o.order_all_id = od.order_id_id AND o.employee_id = e.employee_id AND o.ask_no =:ask_no """, ({'order_no':order_no}))
            respond = cursor.fetchall()
        return respond
    def get_order_no(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT order_no FROM select_data_order WHERE order_no IS NOT NULL;
                """)
            respond = cursor.fetchall()
        return respond
    def get_order_content(self, order_no):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.product_number, p.product_name, od.product_amount FROM select_data_order o, select_data_order_detail od, select_data_product p
                WHERE o.order_all_id = od.order_id_id AND od.product_number_id = p.product_number AND o.order_no = :order_no
                """,({'order_no':order_no}))
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
        respond = {}
        with connection.cursor() as cursor:
            if (kwargs['finished'] == '1') or (kwargs['finished'] == ''):
                command =  """
                    SELECT o.order_no, o.company_number_id, cust.site, cust.contactor, o.expect_date, o.deadline, o.actual_ship_date, o.invoice_condition, o.finished,
                    o.note, o.note1,  p.product_name, odp.product_amount, odp.product_po FROM select_data_order o, select_data_order_detail od, select_data_order_detail_po odp, select_data_customer cust,
                    select_data_product p 
                    WHERE o.order_all_id = od.order_id_id AND o.company_number_id = cust.company_number AND od.product_number_id = p.product_number 
                    """ + " AND o.order_no =:order_no"*(kwargs['order_no'] != '') +\
                    " AND o.company_number_id =:company_number_id "*(kwargs['company_number_id'] != '') +\
                    " AND EXISTS (SELECT 1 FROM select_data_order_detail_po odp WHERE odp.order_detail_id_id = od.order_detail_id)" +\
                    " AND o.deadline =:deadline "*(kwargs['deadline'] != '') +\
                    " AND o.expect_data =:expect_date "*(kwargs['expect_date'] != '') +\
                    " AND ((julianday('now') - julianday(o.deadline)) >=:rest_of_date0) AND (julianday('now') - julianday(o.deadline)) <:rest_of_date1"*(kwargs['rest_of_date0'] != '')
                cursor.execute(command, (kwargs ))
                respond['1'] = cursor.fetchall()
        with connection.cursor() as cursor:
            if  (kwargs['finished'] == '0') or (kwargs['finished'] == ''):
                command =  """
                    SELECT o.order_no, o.company_number_id, cust.site, cust.contactor, o.expect_date, o.deadline, o.actual_ship_date, o.invoice_condition, o.finished,
                    o.note, o.note1,  p.product_name, od.product_amount, NULL FROM select_data_order o, select_data_order_detail od, select_data_customer cust,
                    select_data_product p 
                    WHERE o.order_all_id = od.order_id_id AND o.company_number_id = cust.company_number AND od.product_number_id = p.product_number 
                    """ + " AND o.order_no =:order_no"*(kwargs['order_no'] != '') +\
                    " AND o.company_number_id =:company_number_id "*(kwargs['company_number_id'] != '') +\
                    " AND NOT EXISTS (SELECT 1 FROM select_data_order_detail_po odp WHERE odp.order_detail_id_id = od.order_detail_id)" +\
                    " AND o.deadline =:deadline "*(kwargs['deadline'] != '') +\
                    " AND o.expect_data =:expect_date "*(kwargs['expect_date'] != '') +\
                    " AND ((julianday('now') - julianday(o.deadline)) >=:rest_of_date0) AND (julianday('now') - julianday(o.deadline)) <:rest_of_date1"*(kwargs['rest_of_date0'] != '')
                cursor.execute(command, (kwargs ))
                respond['0'] = cursor.fetchall()
        result = []
        for v in respond.values():
            result.extend(v)
        return result
    def get_vailable_product_po(self, product_number_id):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT DISTINCT osd.product_po FROM select_data_order_stock_product osp, select_data_order_stock_detail osd WHERE osp.product_number_id = :product_number_id AND osp.order_stock_product = osd.order_stock_product_id
            """
            cursor.execute(command, ({'product_number_id':product_number_id}))
            respond = cursor.fetchall()
        return respond

    def update_export_stock_detail(self, **kwargs):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            UPDATE select_data_order_stock_detail SET product_num = product_num - :product_amount WHERE product_po = :product_po
            """
            cursor.execute(command, (kwargs))

    def update_export_order_status(self, **kwargs):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            UPDATE select_data_order SET finished = 1, actual_ship_date = :actual_ship_date, invoice_condition = :invoice_condition WHERE order_all_id IN (SELECT DISTINCT order_id_id FROM 
            (SELECT odp.order_detail_id_id odid, SUM(odp.product_amount) s_amount FROM select_data_order_detail_po odp GROUP BY order_detail_id_id) t1, select_data_order_detail
            WHERE NOT EXISTS ( SELECT 1 FROM select_data_order_detail od WHERE od.product_amount != t1.s_amount AND od.order_detail_id = t1.odid )  AND order_id_id  = :order_id_id )
            """
            cursor.execute(command, (kwargs))
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
    def stock_content_detail(self, stock_po):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT product_number_id, product_po, valid_date, product_num, sd.note FROM select_data_order_stock_product sp, select_data_order_stock_detail sd, select_data_order_stock os
            WHERE
            os.order_stock_po = sp.order_stock_po_id 
            AND
            sp.order_stock_product = sd.order_stock_product_id
            AND
            os.order_stock_po = :stock_po
            """
            cursor.execute(command, {'stock_po':stock_po})
            respond = cursor.fetchall()
        return respond
            
    def stock_content(self, stock_po):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
           SELECT order_stock_date, os.note,  product_number_id, order_num FROM select_data_order_stock os, select_data_order_stock_product sp 
           WHERE 
           os.order_stock_po = sp.order_stock_po_id
           AND
           os.order_stock_po = :stock_po
            """
            cursor.execute(command, {'stock_po':stock_po})
            respond = cursor.fetchall()
        return respond

    def renew_stock_records(self, time_limit):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT os.order_stock_po, os.order_stock_date, os.note, p.product_name, osp.order_num 
            FROM select_data_order_stock os, select_data_order_stock_product osp, select_data_product p  WHERE 
            p.product_number = osp.product_number_id AND osp.order_stock_po_id = os.order_stock_po AND (julianday('now') - julianday(os.last_modified)) <= :time_limit
            """
            cursor.execute(command, {'time_limit':time_limit})
            respond = cursor.fetchall()
        return respond

    def renew_stock_records_detail(self, time_limit):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT os.order_stock_po, os.order_stock_date, osd.note, p.product_name, osd.product_num, osd.product_po, osd.valid_date
            FROM select_data_order_stock os, select_data_order_stock_detail osd,select_data_order_stock_product osp, select_data_product p  WHERE 
            p.product_number = osp.product_number_id AND osp.order_stock_po_id = os.order_stock_po AND osd.order_stock_product_id = osp.order_stock_product 
            AND (julianday('now') - julianday(osd.last_modified)) <= :time_limit
            """
            cursor.execute(command, {'time_limit':time_limit})
            respond = cursor.fetchall()
        return respond
    def update_stock_order_status(self, order_stock_po):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            UPDATE select_data_order_stock SET order_stock_status = 1 WHERE order_stock_po in (SELECT order_stock_po_id FROM (SELECT order_stock_po_id, product_number_id pid, SUM(product_num) spm 
            FROM select_data_order_stock_detail osd, select_data_order_stock_product osp
            WHERE
            osp.order_stock_product = osd.order_stock_product_id
            GROUP BY product_number_id) t 
            WHERE NOT EXISTS (SELECT 1 FROM select_data_order_stock_product osp WHERE osp.product_number_id = t.pid AND osp.order_num != t.spm) 
            AND order_stock_po = :order_stock_po)
            """
            cursor.execute(command, {'order_stock_po':order_stock_po})
    def show_stock(self, t1, t2):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT p.n, IFNULL(td1.spm,0), IFNULL(td2.spm0,0), IFNULL(td4.som1,0) - IFNULL(td1.spm,0) - IFNULL(td2.spm0,0) + IFNULL(td3.som,0) FROM 
            (SELECT product_name n, product_number p_id FROM select_data_product) p LEFT OUTER JOIN
            (SELECT od.product_number_id p_id, SUM(product_amount) spm FROM select_data_order o, select_data_order_detail od 
            WHERE 
            order_status = 1 
            AND od.order_id_id = o.order_all_id  
            AND julianday(o.deadline)-julianday('now')  >= :t1 
            AND julianday(o.deadline)-julianday('now')  < :t2 
            GROUP BY od.product_number_id) td1 ON p.p_id = td1.p_id
            LEFT OUTER JOIN
            (SELECT od.product_number_id p_id, SUM(product_amount) spm0 FROM select_data_order o, select_data_order_detail od 
            WHERE 
            order_status = 0 
            AND od.order_id_id = o.order_all_id 
            AND julianday(o.demand_date)-julianday('now') >= :t1 
            AND julianday(o.demand_date)-julianday('now') < :t2 
            GROUP BY od.product_number_id) td2 on p.p_id = td2.p_id 
            LEFT OUTER JOIN
            (SELECT osp.product_number_id p_id, SUM(osp.order_num) som FROM select_data_order_stock_product osp, select_data_order_stock os 
            WHERE 
            os.order_stock_status = 0
            AND
            osp.order_stock_po_id = os.order_stock_po 
            GROUP BY osp.product_number_id) td3 on p.p_id = td3.p_id
            LEFT OUTER JOIN
            (SELECT osp.product_number_id p_id, SUM(osp.order_num) som1 FROM select_data_order_stock_product osp, select_data_order_stock os 
            WHERE 
            os.order_stock_status = 1
            AND
            osp.order_stock_po_id = os.order_stock_po 
            GROUP BY osp.product_number_id) td4 on p.p_id = td4.p_id
            """
            cursor.execute(command, ({'t1':t1,'t2':t2}))
            result = cursor.fetchall()
        return result
    def show_way_actual_invoiceunshipped(self):
        from django.db import connection
        with connection.cursor() as cursor:
            command = """
            SELECT p.n, IFNULL(t3.som,0), IFNULL(t4.som1,0), IFNULL(t5.spm,0) FROM 
            (SELECT product_name n, product_number FROM select_data_product) p LEFT OUTER JOIN
            (SELECT osp.product_number_id p_id, SUM(osp.order_num) som FROM select_data_order_stock_product osp, select_data_order_stock os 
            WHERE os.order_stock_status = 0 
            AND
            osp.order_stock_po_id = os.order_stock_po 
            GROUP BY osp.product_number_id) t3 on t3.p_id = p.product_number
            LEFT OUTER JOIN
            (SELECT osp.product_number_id p_id, SUM(osp.order_num) som1 FROM select_data_order_stock_product osp, select_data_order_stock os 
            WHERE os.order_stock_status = 1 
            AND
            osp.order_stock_po_id = os.order_stock_po 
            GROUP BY osp.product_number_id) t4 ON t4.p_id = p.product_number
            LEFT OUTER JOIN
            (SELECT od.product_number_id p_id, SUM(product_amount) spm FROM select_data_order o, select_data_order_detail od 
            WHERE order_status = 1 
            AND 
            od.order_id_id = o.order_all_id 
            AND o.invoice_condition = '1' 
            GROUP BY od.product_number_id) t5 on t5.p_id = p.product_number
            """
            cursor.execute(command, )
            result = cursor.fetchall()
        return result
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
    order_stock_status = models.IntegerField(default=0) # 0:下單 1:已到達 2:部分到貨
    note = models.CharField(max_length=50, null=True)
    last_modified = models.DateField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return "訂貨編號:"+ self.order_stock_po + ", 狀態:"+ str(self.order_stock_status)

class Order_stock_product(models.Model):
    order_stock_product = models.AutoField(primary_key=True)
    order_stock_po = models.ForeignKey(Order_stock, on_delete=models.CASCADE)
    product_number = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_num = models.IntegerField()
    note = models.CharField(max_length=50, null=True)
    objects = models.Manager()
    mymanager = StockManager()
    def __str__(self):
        return "訂貨編號:"+ self.order_stock_po + ", 商品" + self.product_number
# order source detail
class Order_stock_detail(models.Model):
    """
    pk: order stock detail
    """
    order_stock_detail_id = models.AutoField(primary_key=True)
    order_stock_product = models.ForeignKey(Order_stock_product, on_delete=models.CASCADE)
    product_po = models.CharField(max_length=50)
    valid_date = models.DateField()
    product_num = models.IntegerField()
    note = models.CharField(max_length=50, null=True)
    order_detail_status = models.BooleanField(default=False)
    last_modified = models.DateField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return "商品批號:" + self.product_po + ", 序號:" + self.order_stock_product + ", 數量" + str(self.product_num) 

# company employee
class Employee(models.Model):
    """
    pk: empolyee id
    """
    employee_id = models.AutoField(primary_key=True)
    employee_name = models.CharField(max_length=50)
    employee_position  = models.CharField(max_length=50)
    employee_state = models.CharField(max_length=10, default=0)
    password = models.CharField(max_length=50, null=True)
    start_time = models.DateField(null=True)
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
    order_status = models.IntegerField(default=0) # 0:預期 1:真實 2:完成
    finished = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null=True)
    last_modified = models.DateField(auto_now=True)
    objects = models.Manager()
    mymanager = OrderManager()

    def __str__(self):
        return  "流水編號:" + str(self.order_all_id) +',詢價單編號' + (str(self.ask_no) if self.ask_no is not None else "missing") + ",訂單編號"  + (str(self.order_no) if self.order_no is not None else "missing") +",訂單狀態:"  + ("完成" if self.finished else "未完成")
# order for each product with amount
class Order_detail(models.Model):
    """
    detail for order
    """
    order_detail_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_number = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_amount = models.IntegerField()
    objects = models.Manager()
    record = OrderManager()
    def __str__(self):
        return  str(self.order_id) + "," + str(self.product_number) + ":" + str(self.product_amount)
# detail for which products come from
class Order_detail_po(models.Model):
    """
    detail for order
    """
    order_detail_po_id = models.AutoField(primary_key=True)
    order_detail_id = models.ForeignKey(Order_detail, on_delete=models.CASCADE)
    product_po = models.CharField(max_length=50)
    product_amount = models.IntegerField()
    objects = models.Manager()
    def __str__(self):
        return  str(self.order_detail_id) + ":" + str(self.product_amount) + "," + str(self.product_po)

###### define form
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name']
class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_name', 'employee_position', 'employee_state', 'start_time']


