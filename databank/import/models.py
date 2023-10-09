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
    Product_Information = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.HS_Code
    

class Unit_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Unit_Code = models.CharField(max_length=50)
    Unit_Name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.Unit_Code
    
class TradersName_ExporterImporter_meta(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    Name = models.CharField(max_length=300)

    def __str__(self):
        return self.Name
    

