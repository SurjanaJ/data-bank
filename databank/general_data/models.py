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

    def __str__(self):
        return (self.Name_Of_The_Plant) + ' ' + (str(self.id))      