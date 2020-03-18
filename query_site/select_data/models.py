from django.db import models
import re
from django.forms import ModelForm


##### define manager (for display purpose)

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
# company table
class Company(models.Model):
    """
    record the company name
    pk: company id
    """
    company_id = models.AutoField( primary_key=True)
    company_name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return "公司:"+self.company_name
    #time = models.DateField('query time')

# factory table
class Factory(models.Model):
    """
    pk : factory id
    foreign key: company id
    """
    factory_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey('Company', on_delete=models.CASCADE) 
    factory_site = models.CharField(max_length=30)
    def __str__(self):
        r = re.sub('公司' , '廠區', str(self.company_id))
        return  r + '-' + str(self.factory_site)

# people table
class People(models.Model):
    """
    pk: people id
    foreign key: factory 
    """
    people_id = models.AutoField( primary_key=True)
    factory_id = models.ForeignKey('Factory', on_delete=models.CASCADE)
    people_name = models.CharField(max_length=30)

    def __str__(self):
        return re.sub( '廠區', '窗口', str(self.factory_id)) + '-' + self.people_name

# product table
class Product(models.Model):
    """
    pk: product id
    """    
    product_id = models.AutoField( primary_key=True)
    product_name = models.CharField(max_length=50)
    product_period = models.IntegerField(null=True, default=0)
    def __str__(self):
        return '產品:'+ self.product_name  + ', 效期為:' + str(self.product_period)
# stock table
class Stock(models.Model):
    """
    pk: stock id
    foreign key: product id
    """
    stock_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    produced_date = models.DateField()
    num_rest = models.IntegerField()
    # now_time = models.DateField('date of today', auto_now=True)    
    record = StockManager()
    def __str__(self):
        r = re.sub('效.*', '', str(self.product_id))
        return  r + ", 庫存個數為:"+str(self.num_rest)

# company employee
class Employee(models.Model):
    """
    pk: empolyee id
    """
    employee_id = models.AutoField( primary_key=True)
    employee_name = models.CharField(max_length=50)
    employee_position  = models.CharField(max_length=50)
    employee_state = models.CharField(max_length=10)
    start_time = models.DateField()
    def __str__(self):
        return "員工名稱:"+self.employee_name
# order table
class Order_get(models.Model):
    """
    pk: order id
    """
    order_id = models.AutoField(primary_key=True)
    #接單日期
    get_order_date = models.DateField()
    po_num = models.CharField(max_length=200)
    finished = models.BooleanField(default=False)
    def __str__(self):
        return "訂單編號:" + self.po_num

# order detail table  
class Order_detail(models.Model):
    """
    pk: detail id
    foreign key: order_id, product_id, reponse_id, custom_id
    """
    detail_id = models.AutoField(primary_key=True)
    # foreign key as product_id
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    # foreign key as order_id
    order_id = models.ForeignKey('Order_get', on_delete=models.CASCADE)
    # foreign key as employee_id
    response_id = models.ForeignKey('Employee', on_delete=models.CASCADE, null = True)
    # foreign key as people_id
    custom_id = models.ForeignKey('People', on_delete=models.CASCADE)
    product_num = models.IntegerField()
    product_require_date = models.IntegerField(null=True)
    other_command = models.CharField(max_length=200, default="No command")
    expected_ship_date = models.DateField()
    actual_ship_date = models.DateField(null=True)
    last_modified = models.DateTimeField(auto_now=True)

    record = InsertManager()
    def __str__(self):
        r = re.sub('效.*', '', str(self.product_id))
        return f"{r}, 產品數量:{self.product_num}"

###### define form
class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['company_name']
class FactoryForm(ModelForm):
    class Meta:
        model = Factory
        fields = ['company_id', 'factory_site']
class PeopleForm(ModelForm):
    class Meta:
        model = People
        fields = ['factory_id', 'people_name']
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_period']
class StockForm(ModelForm):
    class Meta:
        model = Stock
        fields = ['product_id', 'produced_date', 'num_rest']
class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_name', 'employee_position', 'employee_state', 'start_time']
class Order_getForm(ModelForm):
    class Meta:
        model = Order_get
        fields = ['get_order_date', 'po_num', 'finished']

class Order_detailForm(ModelForm):
    class Meta:
        model = Order_detail
        fields = ['product_id', 'order_id', 'response_id', 'custom_id', 'product_num',
         'product_require_date', 'other_command', 'expected_ship_date', 'actual_ship_date']


# class Migration(migrations.Migration):

#     dependencies = [('migrations', '0001_initial')]

#     operations = [
#         migrations.DeleteModel('Tribble'),
#         migrations.AddField('Author', 'rating', models.IntegerField(default=0)),
#     ]