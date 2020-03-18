from django import forms 

class InsertForm(forms.Form):
    company_name = forms.CharField(label = "company_name", max_length=50)
    factory_site = forms.CharField(label = "factory_site", max_length=50)
    people_name = forms.CharField(label = "people_name", max_length=50)
    product_name = forms.CharField(label = "product_name", max_length=50)
    product_amount = forms.IntegerField(label = "product_amount")
    product_demand = forms.CharField(label = "product_demand", max_length=50)
    get_date = forms.DateField(label = "get_date")
    expect_date = forms.DateField(label = "expect_date")
    note = forms.CharField(label = "note")


