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
    Code=models.CharField()
    Land_Type=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.Code


class Land(models.Model):

    Land_Unit_Options=(
        ('Ha','Ha'),
    )


    id=models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta,on_delete=models.CASCADE)
    Land_Code=models.ForeignKey(Land_Code_Meta, on_delete=models.CASCADE)
    Unit=models.CharField(max_length=10, choices=Land_Unit_Options, null=True, blank=True)
    Area=models.DecimalField(max_digits=100, decimal_places=3,blank=True, null=True)

class Transport_Meta(models.Model):
    id=models.AutoField(primary_key=True)
    Code=models.CharField(max_length=100)
    Transport_Type=models.TextField(null=True,blank=True)

class Transport(models.Model):

    Unit_Options=(
        ('Metric Ton', 'Metric Ton'),
    )


    id=models.AutoField(primary_key=True)
    Year=models.DateField(null=True, blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Transport_Classification_Code=models.ForeignKey(Transport_Meta, on_delete=models.CASCADE)
    Unit=models.CharField(max_length=10, choices=Unit_Options, null=True,blank=True)
    Quantity=models.DecimalField(max_digits=100,decimal_places=3,blank=True,null=True)



class Tourism_Meta(models.Model):
    id=models.AutoField(primary_key=True)
    Code=models.CharField(max_length=100)
    Arrival_Mode=models.TextField(null=True,blank=True)

class Tourism(models.Model):
    id=models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='Tourism_Country')
    Number_Of_Tourist = models.IntegerField(null=True,blank=True)
    Nationality_Of_Tourism=models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='Tourism_Nationality_Of_Tourism')
    Arrival_code=models.ForeignKey(Tourism_Meta,on_delete=models.CASCADE)
    Number=models.IntegerField(default=0,null=True,blank=True)


class Hotel(models.Model):
    id=models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Name_Of_The_Hotel=models.CharField(null=True,blank=True)
    Capacity_Room=models.IntegerField(default=0,null=True,blank=True)
    Occupancy_In_Year=models.IntegerField(default=0,null=True,blank=True)
    City = models.CharField(null=True,blank=True)


class Water_Meta(models.Model):
    id=models.AutoField(primary_key=True)
    Code=models.CharField(max_length=100)
    Water_Type=models.TextField(null=True,blank=True)


class Water(models.Model):

    Unit_Options = (
        ('Cu Metre', 'Cu Metre'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Water_Type_Code=models.ForeignKey(Water_Meta,on_delete=models.CASCADE)
    Description = models.CharField(null=True, blank=True)
    Unit=models.CharField(max_length=10, choices=Unit_Options , null=True, blank=True)
    Volume = models.DecimalField(max_digits=100,decimal_places=3,null=True,blank=True)
    Name_Of_The_River = models.CharField(max_length=100,null=True,blank=True)





