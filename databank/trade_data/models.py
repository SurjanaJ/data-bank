from django.db import models

# Create your models here.
class Country_meta(models.Model):
    # id = models.IntegerField(primary_key=True, unique=True, editable=False)
    id = models.AutoField(primary_key=True)
    Country_Name = models.CharField(max_length=200)
    Country_Code_2 = models.CharField(max_length=3, null=True, blank=True)
    Country_Code_3 = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return self.Country_Name
    
class HS_Code_meta(models.Model):   
    id = models.AutoField(primary_key=True)
    HS_Code = models.CharField(max_length=100)
    Product_Information = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.HS_Code
    

class Unit_meta(models.Model):
    id = models.AutoField(primary_key=True)
    Unit_Code = models.CharField(max_length=50)
    Unit_Name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.Unit_Code
       

class TradeData(models.Model):
    TRADE_OPTIONS = (
        ('Import', 'Import'),
        ('Export', 'Export')
    )
    id = models.AutoField(primary_key=True)
    Trade_Type = models.CharField(max_length=100, choices=TRADE_OPTIONS, null=True, blank=True) 
    Calender = models.DateField(null=True, blank=True)
    Fiscal_Year = models.CharField(max_length=10, null=True, blank=True)
    Duration = models.CharField(max_length=100, null=True, blank=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='tradedata_country')
    HS_Code = models.ForeignKey(HS_Code_meta, on_delete=models.CASCADE)
    Unit = models.ForeignKey(Unit_meta, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=0, null=True, blank=True)
    Currency_Type = models.CharField(max_length=100, null=True, blank=True)
    Amount = models.DecimalField(max_digits=100, decimal_places=3,null=True, blank=True)
    Tarrif = models.DecimalField(max_digits=100, decimal_places=3, null=True, blank=True, default=None)
    Origin_Destination =  models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='tradedata_origin_destination')
    TradersName_ExporterImporter = models.CharField(max_length=100, null=True, blank=True)
    DocumentsLegalProcedural = models.CharField(max_length=300, null=True, blank=True)
    

    def __str__(self):
        return (str(self.id))