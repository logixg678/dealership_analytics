# logix_analytics/models.py
from django.db import models

class Dealership(models.Model):
    dealershipsk = models.AutoField(primary_key=True, db_column='DealershipSK', verbose_name='Dealership SK')
    dealership_id = models.CharField(unique=True, max_length=50, db_column='Dealership_ID', verbose_name='Original Dealership ID')
    dealername = models.CharField(max_length=100, db_column='DealerName', verbose_name='Dealer Name')
    area = models.CharField(max_length=50, blank=True, null=True, db_column='Area')

    class Meta:
        managed = False
        db_table = 'Dealership'
        verbose_name = "Dealership"
        verbose_name_plural = "Dealerships"

    def __str__(self):
        return self.dealername

class DealershipContact(models.Model):
    dealershipcontactsk = models.AutoField(primary_key=True, db_column='DealershipContactSK', verbose_name='Contact SK')
    # ForeignKey mapping: Django field name 'dealership' will look for 'dealership_id' column by default.
    # We use db_column to specify the actual FK column name if it's different from 'dealership_id'.
    # Here, 'dealershipsk' in DealershipContact model links to Dealership.dealershipsk (PK)
    dealership = models.ForeignKey(Dealership, on_delete=models.CASCADE, db_column='DealershipSK', verbose_name='Dealership')
    contactname = models.CharField(max_length=150, blank=True, null=True, db_column='ContactName', verbose_name='Contact Name')
    role = models.CharField(max_length=100, blank=True, null=True, db_column='Role')
    email = models.EmailField(max_length=255, blank=True, null=True, db_column='Email')
    phone = models.CharField(max_length=30, blank=True, null=True, db_column='Phone')

    class Meta:
        managed = False
        db_table = 'DealershipContact'
        verbose_name = "Dealership Contact"
        verbose_name_plural = "Dealership Contacts"

    def __str__(self):
        return f"{self.contactname or 'N/A'} ({self.dealership.dealername})"

class StatusLookup(models.Model):
    statussk = models.AutoField(primary_key=True, db_column='StatusSK', verbose_name='Status SK')
    statuscode = models.CharField(unique=True, max_length=10, db_column='StatusCode', verbose_name='Status Code')
    statustext = models.CharField(max_length=255, db_column='StatusText', verbose_name='Status Text')
    statusgrouping = models.CharField(max_length=100, db_column='StatusGrouping', verbose_name='Status Grouping')
    statussortorder = models.PositiveSmallIntegerField(db_column='StatusSortOrder', verbose_name='Sort Order')

    class Meta:
        managed = False
        db_table = 'StatusLookup'
        verbose_name = "Status Lookup"
        verbose_name_plural = "Status Lookups"
        ordering = ['statussortorder']

    def __str__(self):
        return f"{self.statuscode} - {self.statustext}"

class FeatureLookup(models.Model):
    featuresk = models.AutoField(primary_key=True, db_column='FeatureSK', verbose_name='Feature SK')
    featurename = models.CharField(unique=True, max_length=150, db_column='FeatureName', verbose_name='Feature Name')
    featurecategory = models.CharField(max_length=50, blank=True, null=True, db_column='FeatureCategory', verbose_name='Category')

    class Meta:
        managed = False
        db_table = 'FeatureLookup'
        verbose_name = "Feature Lookup"
        verbose_name_plural = "Feature Lookups"

    def __str__(self):
        return self.featurename

class Vehicle(models.Model):
    vehiclesk = models.AutoField(primary_key=True, db_column='VehicleSK', verbose_name='Vehicle SK')
    vin = models.CharField(unique=True, max_length=17, blank=True, null=True, db_column='VIN')
    dealership = models.ForeignKey(Dealership, on_delete=models.SET_NULL, blank=True, null=True, db_column='DealershipSK', verbose_name='Dealership')
    materialdesc_source = models.CharField(max_length=255, blank=True, null=True, db_column='MaterialDesc_Source', verbose_name='Source Material Desc')
    modelname = models.CharField(max_length=100, blank=True, null=True, db_column='ModelName', help_text="Parsed by DB trigger")
    bodystyle = models.CharField(max_length=150, blank=True, null=True, db_column='BodyStyle', help_text="Parsed by DB trigger")
    seatconfiguration = models.CharField(max_length=20, blank=True, null=True, db_column='SeatConfiguration', help_text="Parsed by DB trigger")
    modelyear = models.IntegerField(blank=True, null=True, db_column='ModelYear', help_text="Parsed by DB trigger (e.g., 2024)")
    trimlevel = models.CharField(max_length=100, blank=True, null=True, db_column='TrimLevel', verbose_name='Trim Level')
    plantcode = models.CharField(max_length=10, blank=True, null=True, db_column='PlantCode', verbose_name='Plant Code')
    basemsrp = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_column='BaseMSRP', verbose_name='Base MSRP')
    dealercost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_column='DealerCost', verbose_name='Dealer Cost')
    currentstatus = models.ForeignKey(StatusLookup, on_delete=models.RESTRICT, db_column='CurrentStatusSK', blank=True, null=True, verbose_name='Current Status')
    currentstatusdate = models.DateField(blank=True, null=True, db_column='CurrentStatusDate', verbose_name='Current Status Date')
    stockcategory = models.CharField(max_length=50, blank=True, null=True, db_column='StockCategory', verbose_name='Stock Category')
    stocktype = models.CharField(max_length=20, blank=True, null=True, db_column='StockType', verbose_name='Stock Type')
    
    features = models.ManyToManyField(FeatureLookup, through='VehicleFeature', related_name='vehicles')

    class Meta:
        managed = False
        db_table = 'Vehicle'
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return self.vin or f"VehicleSK_{self.vehiclesk}"

class SalesOrder(models.Model):
    salesordersk = models.AutoField(primary_key=True, db_column='SalesOrderSK', verbose_name='Sales Order SK')
    salesorderno = models.CharField(unique=True, max_length=50, blank=True, null=True, db_column='SalesOrderNo', verbose_name='Sales Order No')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.RESTRICT, db_column='VehicleSK', verbose_name='Vehicle') # Changed from vehiclesk for clarity
    dealership = models.ForeignKey(Dealership, on_delete=models.RESTRICT, db_column='DealershipSK', verbose_name='Dealership') # Changed for clarity
    orderdate = models.DateField(blank=True, null=True, db_column='OrderDate', verbose_name='Order Date')
    retaildate = models.DateField(blank=True, null=True, db_column='RetailDate', verbose_name='Retail Date')
    pickupdate = models.DateField(blank=True, null=True, db_column='PickupDate', verbose_name='Pickup Date')
    deliverydate = models.DateField(blank=True, null=True, db_column='DeliveryDate', verbose_name='Delivery Date')

    class Meta:
        managed = False
        db_table = 'SalesOrder'
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"

    def __str__(self):
        return self.salesorderno or f"OrderSK_{self.salesordersk}"

class VehicleFeature(models.Model):
    # For a `through` model that Django manages (even with managed=False on the main models),
    # it's often simpler to let Django add its own 'id' primary key.
    # The unique_together constraint will enforce your composite key logic.
    # If you strictly want to map the composite PK, it's more complex with `managed=False`.
    # Let's try with Django's default PK for this junction table first for simplicity with ManyToManyField.
    # If we need to reflect the exact composite PK from the DB, we can adjust.
    
    # Original approach:
    # vehiclesk = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='VehicleSK', primary_key=True) # Part of composite PK
    # featuresk = models.ForeignKey(FeatureLookup, on_delete=models.RESTRICT, db_column='FeatureSK') # Part of composite PK
    
    # Simpler approach for `through` model:
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='VehicleSK')
    feature = models.ForeignKey(FeatureLookup, on_delete=models.RESTRICT, db_column='FeatureSK') # Changed from featuresk for clarity
    selectedoptionvalue = models.CharField(max_length=255, db_column='SelectedOptionValue', verbose_name='Selected Option')

    class Meta:
        managed = False
        db_table = 'VehicleFeature'
        unique_together = (('vehicle', 'feature'),) # Reflects composite PK uniqueness in DB
        verbose_name = "Vehicle Feature"
        verbose_name_plural = "Vehicle Features"

    def __str__(self):
        return f"{self.vehicle} - {self.feature}: {self.selectedoptionvalue}"