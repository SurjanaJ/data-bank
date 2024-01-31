from django.db import models
from trade_data.models import Country_meta, Unit_meta

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

    def __str__(self):
        return self.Code

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

    def __str__(self):
        return self.Code

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


class Public_Unitillity(models.Model):
    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Type_Of_Public_Utility = models.CharField(max_length = 100,null= True,blank = True)
    Number = models.IntegerField(default=0,null=True,blank=True)


class Mine_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code=models.CharField(max_length=100)
    Mine_Type=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.Mine_Type
    

class Mining(models.Model):

    Unit_Options = (
        ('Mt', 'Mt'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Name_Of_Mine=models.ForeignKey(Mine_Meta,on_delete=models.CASCADE)
    Unit = models.CharField(max_length = 10, choices=Unit_Options , null=True, blank=True)
    Current_Production = models.IntegerField(default=0,null=True,blank=True)
    Potential_Stock = models.IntegerField(default=0,null=True,blank=True)
    Mining_Company_Name = models.CharField(max_length=100,null=True,blank=True)

class Energy_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = Code=models.CharField(max_length=100)
    Energy_Type = models.TextField(null=True,blank=True)


class Energy(models.Model):

    Potential_Unit_Options = (
        ('Mt','Mt'),
    )

    Unit_Production_Options = (
        ('Megawat','Megawat'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Power_Category_Code = models.ForeignKey(Energy_Meta,on_delete = models.CASCADE)
    Potential_Unit = models.CharField(max_length = 10, choices = Potential_Unit_Options, null = True , blank = True)
    Potential_Capacity_MW = models.IntegerField(default = 0 , blank=True , null = True)
    Unit_Production = models.CharField(max_length = 20, choices = Unit_Production_Options , blank = True , null = True)
    Current_Production_In_MW = models.IntegerField(default = 0 , null = True , blank = True)
    Name_Of_The_Generating_Company = models.CharField(max_length = 100 , null = True , blank = True)

class Road_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = Code=models.CharField(max_length=100)
    Road_Type = models.TextField(null=True,blank=True)


class Road(models.Model):

    Length_Unit = (
        ('KM','KM'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Highway_No = models.CharField(max_length = 50 , null = True , blank = True)
    Name_Of_The_Road = models.CharField(max_length = 50 , null = True , blank = True)
    Code_Type_Of_Road = models.ForeignKey(Road_Meta, on_delete = models.CASCADE)
    Length_Unit = models.CharField(max_length=20, choices = Length_Unit, blank = True ,null = True)
    Length = models.IntegerField(default = 0 , null = True , blank = True)



class Housing_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = Code=models.CharField(max_length=100)
    House_Type = models.TextField(null=True,blank=True)

class Housing(models.Model):

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    House_Code = models.ForeignKey(Housing_Meta,on_delete = models.CASCADE)
    City = models.CharField(null=True,blank=True)
    Number = models.IntegerField(default = 0 , null = True , blank = True)


class Health_disease_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = Code=models.CharField(max_length=100)
    Deasease_Type = models.TextField(null=True,blank=True)


class Health_disease(models.Model):

    Unit_Options = (
        ('Person','Person'),
    )

    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Desease_Code = models.ForeignKey( Health_disease_Meta, on_delete = models.CASCADE )
    Unit = models.CharField(max_length = 20 , choices = Unit_Options , blank = True , null= True)
    Number_Of_Case = models.IntegerField(default = 0 , null = True , blank = True)


class Budgetary_Data(models.Model):
    id = models.AutoField(primary_key=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Fiscal_Year = models.CharField(max_length=10, null=True, blank=True)
    Amount_In_USD = models.IntegerField(default = 0 , null = True ,blank = True)
    Prefered_Denomination = models.CharField(max_length = 30 , null = True , blank = True)
 

class Political_Data(models.Model):
    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Political_Party_Name = models.CharField(max_length = 30,null = True , blank = True)
    Number_Of_Member = models.IntegerField(default = 0 ,null = True ,blank = True)
    Province =  models.CharField(max_length = 30,null = True , blank = True)
    District =  models.CharField(max_length = 30,null = True , blank = True)
    Municipality = models.CharField(max_length = 30 ,null = True ,blank = True)
    Wards =  models.CharField(max_length = 30,null = True , blank = True)


class Disaster_Data_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = Code=models.CharField(max_length=100)
    Disaster_Type = models.TextField(null=True,blank=True)
    

class Disaster_Data(models.Model):
    id = models.AutoField(primary_key=True)
    Year=models.DateField(null=True,blank=True)
    Country=models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Disaster_Code = models.ForeignKey(Disaster_Data_Meta,on_delete= models.CASCADE)
    Human_Loss = models.IntegerField(default = 0 ,null = True ,blank = True)
    Animal_Loss = models.IntegerField(default = 0 ,null = True ,blank = True)
    Physical_Properties_Loss_In_USD = models.IntegerField(default = 0 ,null = True ,blank = True)


class Services_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=100)
    Services_Type = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.Code

class Services(models.Model):
    DIRECTION_OPTIONS = (
        ('Import', 'Import'),
        ('Export', 'Export')
    )
    id = models.AutoField(primary_key=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='services_country')
    Year = models.DateField(null=True, blank=True)
    Direction = models.CharField(max_length= 10, choices = DIRECTION_OPTIONS, null=True, blank=True )
    Code = models.ForeignKey(Services_Meta, on_delete = models.CASCADE)
    Value = models.FloatField(max_length=100,null=True, blank=True)
    Origin_Destination = models.ForeignKey(Country_meta, on_delete=models.CASCADE, related_name='services_origin_destination')


class Crime_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField(max_length= 100)
    Name = models.TextField(blank= True, null = True)
    
    def __str__(self):
        return self.Code
    
class Crime(models.Model):
    GENDER_OPTIONS = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    id = models.AutoField(primary_key=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Year = models.DateField(null=True, blank=True)
    Code = models.ForeignKey(Crime_Meta, on_delete= models.CASCADE)
    Gender = models.CharField(max_length= 10, choices = GENDER_OPTIONS, null=True, blank=True )
    Age = models.IntegerField(null=True, blank=True)
    District = models.CharField(max_length= 50, null=True, blank=True )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Education_Level_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField(max_length= 20)
    Level = models.TextField(blank= True, null= True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Code

class Education_Degree_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField(max_length= 20)
    Degree = models.TextField(null=True, blank= True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Code

class Education(models.Model):
    id = models.AutoField(primary_key=True)
    Level_Code = models.ForeignKey(Education_Level_Meta, on_delete= models.CASCADE)
    Degree_Code = models.ForeignKey(Education_Degree_Meta, on_delete = models.CASCADE)
    Male = models.BigIntegerField(default = 0)
    Female = models.BigIntegerField(default = 0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class Occupation_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    SOC_Code = models.CharField(max_length= 100)
    SOC_Group = models.TextField(blank= True, null = True)
    SOC_Title = models.TextField(blank= True, null = True)
    
    def __str__(self):
        return self.SOC_Code
    
class Occupation(models.Model):
    id = models.AutoField(primary_key=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Year = models.IntegerField()
    Code = models.ForeignKey(Occupation_Meta, on_delete= models.CASCADE)
    Number = models.IntegerField()

    def __str__(self):
        return self.Code
    

class Climate_Place_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Place_Code = models.CharField(max_length=20)
    Place_Name = models.TextField()
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Place_Code

class Climate_Data(models.Model):
    CLIMATE_OPTIONS = (
        ('Rain', 'Rain'),
        ('Snow', 'Snow'),
        ('Storm', 'Storm')
    )
   
    id = models.AutoField(primary_key=True)
    Country = models.ForeignKey(Country_meta, on_delete=models.CASCADE)
    Date =models.DateField()
    Place = models.ForeignKey(Climate_Place_Meta, on_delete=models.CASCADE)
    Temperature_Unit = models.ForeignKey(Unit_meta, on_delete = models.CASCADE,related_name='generaldata_temperature_unit')
    Max_Temperature = models.FloatField(max_length=100)
    Min_Temperature = models.FloatField(max_length=100)
    Climate=models.CharField(max_length=20,choices=CLIMATE_OPTIONS)
    Climate_Unit = models.ForeignKey(Unit_meta, on_delete = models.CASCADE, related_name='generaldata_climate_unit')
    Amount =  models.FloatField(max_length=100)

    def __str__(self):
        return (str(self.id))


class Currency_Meta(models.Model):
    id = models.AutoField(primary_key=True)
    Currency_Name = models.TextField()
    Currency_Code = models.CharField(max_length = 40)
    Country = models.ForeignKey(Country_meta, on_delete= models.CASCADE)

    def __str__(self):
        return (self.Currency_Name)
