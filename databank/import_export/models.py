from django.db import models

# Create your models here.

class Country_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Country_Name = models.CharField(max_length=200)
    Country_Code_2 = models.CharField(max_length=2, null=True, blank=True)
    Country_Code_3 = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return self.Country_Name


class HS_Code_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    HS_Code = models.CharField(max_length=100)
    Name = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.HS_Code


class Unit_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Unit_Code = models.CharField(max_length=50, null=True, blank=True)
    Unit_Name = models.CharField(max_length=200)

    def __str__(self):
        return self.Unit_Name

class Traders_Name__Exporter_Importer_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Name = models.CharField(max_length=300)

    def __str__(self):
        return self.Name


class TradeData(models.Model):
    TRADE_OPTIONS = (
        ('import', 'import'),
        ('export', 'export')
    )
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Trade_Type = models.CharField(max_length=100, choices=TRADE_OPTIONS, null=True, blank=True) 
    Calender = models.CharField(max_length=5,null=True, blank=True)
    Fiscal_Year = models.CharField(max_length=10, null=True, blank=True)
    Duration = models.IntegerField(default=0, null=True, blank=True)
    Country_Name = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    HS_Code = models.ForeignKey(HS_Code_meta, on_delete=models.CASCADE)
    Unit = models.ForeignKey(Unit_meta, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=0, null=True, blank=True)
    Currency_Type = models.CharField(max_length=100, null=True, blank=True)
    Amount = models.DecimalField(max_digits=100, decimal_places=3,null=True, blank=True)
    Tarrif = models.DecimalField(max_digits=100, decimal_places=3, null=True, blank=True)
    Origin_Destination = models.CharField(max_length=200, null=True, blank=True)
    Traders_Name__Exporter_Importer = models.ForeignKey(Traders_Name__Exporter_Importer_meta, null=True, blank=True)
    Documents = models.CharField(max_length=300, null=True, blank=True)
    Product_Information = models.TextField(null=True, blank=True)



