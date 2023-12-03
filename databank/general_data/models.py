from django.db import models
from trade_data.models import Country_meta

# # Create your models here.
class ForestData(models.Model):
    Stock_Unit_Options=(
        ('Cu Mtr','Cu Mtr'),
    )
    Area_Unit_Options=(
        ('Hector','Hector'),
    )
    id = models.AutoField(primary_key=True)
    Year = models.DateField(null=True, blank=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Name_Of_The_Plant = models.CharField(max_length= 100)
    Scientific_Name = models.CharField(max_length=100)
    Local_Name = models.CharField(max_length=100)
    Stock_Unit = models.CharField(max_length=50,choices=Stock_Unit_Options, null=True, blank=True)
    Stock_Available = models.IntegerField(default=0, null=True, blank=True)
    Area_Unit = models.CharField(max_length=100, choices=Area_Unit_Options, blank=True, null=True)
    Area_Covered = models.DecimalField(max_digits=100, decimal_places=3,blank=True, null=True)

        
class PopulationData(models.Model):

    Gender_Options=(
        ('Male','Male'),
        ('Female','Female')
    )

    Age_Group_Options=(
        ('0-14','0-14'),
        ('15-64','15-64'),
        ('64+','64+'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True, blank=True)
    Country=models.ForeignKey(Country_meta,on_delete=models.CASCADE)
    Gender=models.CharField(max_length=10,choices=Gender_Options, null=True,blank=True)
    Age_Group=models.CharField(max_length=10,choices=Age_Group_Options, null=True, blank=True)
    Population=models.IntegerField(default=0,blank=True,null=True)


class Land_Code_Meta(models.Model):
    id=models.AutoField(primary_key=True)
    Code=models.CharField(max_length=100)
    Land_Type=models.TextField(null=True,blank=True)


class Land(models.Model):

    Land_Unit_Options=(
        ('Ha','Ha'),
    )


    id=models.AutoField(primary_key=True)
    year=models.DateField(null=True,blank=True)
    Land_Code=models.ForeignKey(Land_Code_Meta, on_delete=models.CASCADE)
    Unit=models.CharField(max_length=10, choices=Land_Unit_Options, null=True, blank=True)
    Area=models.DecimalField(max_digits=100, decimal_places=3,blank=True, null=True)



