# logix_analytics/admin.py
from django.contrib import admin
from .models import (
    Dealership,
    DealershipContact,
    StatusLookup,
    FeatureLookup,
    Vehicle,
    SalesOrder,
    VehicleFeature
)

# Basic registration (to get started)
# admin.site.register(Dealership)
# admin.site.register(DealershipContact)
# admin.site.register(StatusLookup)
# admin.site.register(FeatureLookup)
# admin.site.register(Vehicle)
# admin.site.register(SalesOrder)
# admin.site.register(VehicleFeature)

# --- More customized admin interfaces ---

@admin.register(Dealership)
class DealershipAdmin(admin.ModelAdmin):
    list_display = ('dealername', 'dealership_id', 'area')
    search_fields = ('dealername', 'dealership_id', 'area')
    list_filter = ('area',)

@admin.register(DealershipContact)
class DealershipContactAdmin(admin.ModelAdmin):
    list_display = ('contactname', 'dealership', 'role', 'email', 'phone')
    search_fields = ('contactname', 'dealership__dealername', 'email', 'role')
    list_filter = ('dealership__dealername', 'role')
    autocomplete_fields = ['dealership'] # For easier selection if you have many dealerships

@admin.register(StatusLookup)
class StatusLookupAdmin(admin.ModelAdmin):
    list_display = ('statuscode', 'statustext', 'statusgrouping', 'statussortorder')
    search_fields = ('statuscode', 'statustext', 'statusgrouping')
    list_filter = ('statusgrouping',)
    ordering = ('statussortorder',)

@admin.register(FeatureLookup)
class FeatureLookupAdmin(admin.ModelAdmin):
    list_display = ('featurename', 'featurecategory')
    search_fields = ('featurename', 'featurecategory')
    list_filter = ('featurecategory',)

# For VehicleFeature, an inline representation within Vehicle is often better
class VehicleFeatureInline(admin.TabularInline): # Or admin.StackedInline
    model = VehicleFeature
    extra = 1 # Number of empty forms to display
    autocomplete_fields = ['feature'] # If you have many features

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'vin',
        'modelname',
        'modelyear',
        'dealership',
        'currentstatus',
        'stockcategory',
        'basemsrp'
    )
    search_fields = (
        'vin',
        'modelname',
        'materialdesc_source',
        'dealership__dealername',
        'trimlevel'
    )
    list_filter = (
            'modelyear',
            'stockcategory',
            'stocktype',
            'dealership__dealername',
            ('currentstatus', admin.RelatedFieldListFilter), # <--- CORRECTED
        )
    readonly_fields = ( # Fields parsed by DB trigger should ideally be read-only in admin
        'modelname',
        'bodystyle',
        'seatconfiguration',
        'modelyear',
    )
    autocomplete_fields = ['dealership', 'currentstatus']
    inlines = [VehicleFeatureInline] # To manage vehicle features directly on the vehicle page
    fieldsets = (
        (None, {
            'fields': ('vin', 'dealership', 'materialdesc_source', 'trimlevel', 'plantcode')
        }),
        ('Parsed Information (Read-Only from DB Trigger)', {
            'fields': ('modelname', 'bodystyle', 'seatconfiguration', 'modelyear'),
            'classes': ('collapse',), # Makes this section collapsible
        }),
        ('Pricing', {
            'fields': ('basemsrp', 'dealercost')
        }),
        ('Status & Stock', {
            'fields': ('currentstatus', 'currentstatusdate', 'stockcategory', 'stocktype')
        }),
    )

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('salesorderno', 'vehicle', 'dealership', 'orderdate', 'retaildate')
    search_fields = ('salesorderno', 'vehicle__vin', 'dealership__dealername')
    list_filter = ('orderdate', 'retaildate', 'dealership__dealername')
    autocomplete_fields = ['vehicle', 'dealership']
    date_hierarchy = 'orderdate' # Adds a date drill-down navigation

# Register VehicleFeature separately if you want a dedicated admin page for it,
# though managing it via VehicleInline is usually more practical.
# If you register it here, you might want to remove the VehicleFeatureInline from VehicleAdmin
# or just use it for a different view of the data.
@admin.register(VehicleFeature)
class VehicleFeatureAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'feature', 'selectedoptionvalue')
    search_fields = ('vehicle__vin', 'feature__featurename', 'selectedoptionvalue')
    autocomplete_fields = ['vehicle', 'feature']