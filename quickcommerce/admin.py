from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.shortcuts import render
from django.db.models import Sum, Count

from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django import forms
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from .models import *


# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'display_image', 'gallery_link')
#     readonly_fields = ('display_image',)

#     def display_image(self, obj):
#         """Display the main product image in the admin."""
#         if obj.image:
#             return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
#         return "No Image"
    
#     display_image.short_description = "Main Image"
    
#     def gallery_link(self, obj):
#         """Provide a link to open the gallery in a popup."""
#         url = reverse('admin:product_gallery', args=[obj.pk])
#         return format_html('<a href="{}" class="button" target="_blank">View Gallery</a>', url)
    
#     gallery_link.short_description = "Product Gallery"
    
#     def get_urls(self):
#         """Add custom URLs for managing the product gallery in admin."""
#         urls = super().get_urls()
#         custom_urls = [
#             path('gallery/<int:product_id>/', self.admin_site.admin_view(self.product_gallery), name='product_gallery'),
#             path('gallery/delete/<int:image_id>/', self.admin_site.admin_view(self.delete_gallery_image), name='delete_gallery_image'),
#         ]
#         return custom_urls + urls

#     def product_gallery(self, request, product_id):
#         """Display the product gallery images in a popup."""
#         product = get_object_or_404(Product, pk=product_id)
#         images = ProductImage.objects.filter(product=product)

#         if request.method == 'POST':
#             # Handle main image upload
#             if 'main_image' in request.FILES:
#                 product.image = request.FILES['main_image']
#                 product.save()
#                 return redirect('admin:product_gallery', product_id=product.id)

#             # Handle gallery image upload
#             elif 'gallery_image' in request.FILES:
#                 ProductImage.objects.create(product=product, image=request.FILES['gallery_image'])
#                 return redirect('admin:product_gallery', product_id=product.id)

#         context = {
#             'product': product,
#             'images': images,
#         }
#         return TemplateResponse(request, 'admin/product_gallery.html', context)

#     def delete_gallery_image(self, request, image_id):
#         """Handle gallery image deletion."""
#         image = get_object_or_404(ProductImage, pk=image_id)
#         product_id = image.product.id
#         image.delete()
#         return redirect('admin:product_gallery', product_id=product_id)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'is_active', 'created_at', 'display_image')
    list_filter = ('place', 'is_active', 'created_at')
    search_fields = ('title', 'tagline', 'button_text', 'place')
    readonly_fields = ('created_at',)
    actions = ['deactivate_banners']

    class Media:
        js = ('admin/js/banner_custom.js',)

    def display_image(self, obj):
        """Display the banner image in the admin."""
        if obj.image:
            return format_html('<img src="{}" width="100" height="50" />'.format(obj.image.url))
        return "No Image"
    
    display_image.short_description = "Banner Image"

    def deactivate_banners(self, request, queryset):
        """Admin action to deactivate selected banners."""
        queryset.update(is_active=False)
    deactivate_banners.short_description = "Deactivate selected banners"

    def get_form(self, request, obj=None, **kwargs):
        """Customize the form for different types of banners."""
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.place == 'primary':  # Main banner
            form.base_fields['button_text'].required = True
            form.base_fields['button_link'].required = True
        else:
            form.base_fields['button_text'].required = False
            form.base_fields['button_link'].required = False
        return form

# Modify the existing UserAdmin
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'phone_number', 'total_amount_spent', 'last_login', 'date_joined', 'display_groups')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'phone_number')
    readonly_fields = ('last_login', 'date_joined', 'total_amount_spent')

    # Define how fields are grouped in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number', 'total_amount_spent')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password1', 'password2', 'is_active', 'is_staff', 'groups')}
        ),
    )

    ordering = ('email',)

    # Helper method to display groups in the list display
    def display_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])
    display_groups.short_description = 'Groups'


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount_percentage', 'max_discount_amount', 'valid_from', 'valid_until', 'is_active')
    search_fields = ('code', 'description')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    filter_horizontal = ('specific_products', 'exclude_products', 'specific_categories', 'exclude_categories')
    
    # Customize fields displayed in the detail view
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'discount_percentage', 'max_discount_amount', 'valid_from', 'valid_until', 'is_active')
        }),
        ('Usage Restrictions', {
            'fields': ('minimum_spend', 'individual_use', 'exclude_sale_items', 'specific_products', 'exclude_products', 'specific_categories', 'exclude_categories')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit_per_coupon', 'usage_limit_per_user')
        }),
    )
    
    ordering = ('-valid_from',)


# Custom StoreAdmin to manage the Store model in the admin interface
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'owner_contact', 'commission_rate', 'is_featured')  # Display these fields in the list view
    search_fields = ('name', 'owner_name', 'owner_contact','contact_person_name')  # Allow search by store name and owner name
    list_filter = ('is_featured', 'categories', 'brands')

    # Group fields into sections for better organization
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'display_image', 'inventory_software', 'commission_rate', 'is_featured', 'categories', 'brands')
        }),
        ('Address Information', {
            'fields': ('street_address', 'city', 'state', 'pin_code', 'country')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Contact Information', {
            'fields': ('owner_name', 'owner_contact', 'contact_person_name', 'contact_person_number')
        }),
    )
    filter_horizontal = ('categories', 'brands')
    # Make slug read-only and automatically filled
    readonly_fields = ('slug',)

# Inline admin for AttributeValue, allowing them to be edited within the Attribute admin view
class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1  # Number of empty fields to display for adding new values
    fields = ('value',)
    verbose_name = 'Attribute Value'
    verbose_name_plural = 'Attribute Values'

# Admin view for Attribute
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','display_values')  # Display these fields in the list view
    search_fields = ('name',)  # Allow search by attribute name
    inlines = [AttributeValueInline]  # Include AttributeValue as inline form for the Attribute model

    def display_values(self, obj):
        return ", ".join([value.value for value in obj.values.all()])
    
    display_values.short_description = 'Values'



# Custom admin view for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at', 'updated_at')  # Display name, logo, parent, and timestamps
    search_fields = ('name',)  # Allow search by category name
    list_filter = ('parent',)  # Allow filtering by parent category
    readonly_fields = ('created_at', 'updated_at')  # Make timestamps read-only
    fields = ('name', 'description', 'parent', 'created_at', 'updated_at')  # Show fields in form


# Custom admin view for Brand
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_logo', 'created_at', 'updated_at')  # Display name, logo, and timestamps
    search_fields = ('name',)  # Allow search by brand name
    readonly_fields = ('created_at', 'updated_at')  # Make timestamps read-only
    fields = ('name', 'logo', 'description', 'created_at', 'updated_at')  # Show fields in form

    # Method to display the logo image in the admin list view
    def display_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.logo.url)
        return "No Logo"
    
    display_logo.short_description = 'Logo'  # Set column header name for the logo

# class InventoryInline(admin.TabularInline):
#     model = Inventory
#     extra = 1  # Number of empty fields to display for adding new inventory
#     fields = ('store', 'quantity', 'last_updated')  # Display these fields in the form
#     readonly_fields = ('last_updated',)

# Inline admin for managing the product gallery (ProductImage) directly from the Product admin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty fields to display for adding new images
    fields = ('image',)  # Display image and thumbnail in the form
   
    
    # Override save to automatically assign the product foreign key
    def save_new_instance(self, form, commit=True):
        instance = form.save(commit=False)
        if self.instance:
            instance.product = self.instance  # Automatically set the product foreign key
        if commit:
            instance.save()
        return instance
    

# Admin view for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'store', 'mrp', 'sale_price', 'display_image', 'created_at')  # Display these fields in the list view
    search_fields = ('name', 'category__name', 'brand__name', 'store__name')  # Enable search by product, category, brand, or store
    list_filter = ('category', 'brand', 'store')  # Enable filtering by category, brand, and store
    readonly_fields = ('slug', 'display_image','display_gallery','created_at')  # Make slug and creation date read-only
    fields = ('name', 'slug', 'inventory', 'description', 'mrp', 'sale_price', 'category', 'brand', 'store', 'image','display_image','display_gallery', 'attributes', 'created_at')  # Display these fields in the form
    # Add ProductImage as an inline for managing product gallery
    inlines = [ProductImageInline]

    # Enable multi-select for product gallery
    filter_horizontal = ('attributes',)

    # Method to display the main product image in the admin list view
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    
    display_image.short_description = "Main Image"

    # Method to display the gallery images as thumbnails in the product form
    def display_gallery(self, obj):
        gallery_images = obj.gallery.all()  # Get all the images in the gallery
        if gallery_images:
            images_html = ''.join([format_html('<img src="{}" width="50" height="50" style="margin: 2px; object-fit: cover;" />', image.image.url) for image in gallery_images])
            return mark_safe(images_html)  # Mark the HTML as safe
        return "No Gallery Images"
    
    display_gallery.short_description = "Product Gallery"

# Inline admin for managing OrderItems
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty fields to display for adding new order items

# Inline admin for managing Payments
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0  # Since it's a one-to-one relation, no extra fields needed

# Admin view for Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'order_status', 'payment_status', 'placed_at', 'updated_at')
    search_fields = ('user__email', 'id')  # Enable search by user email or order ID
    list_filter = ('order_status', 'payment_status', 'placed_at')  # Enable filtering by order status, payment status, and date
    readonly_fields = ('placed_at', 'updated_at', 'tracking_id', 'delivery_status')  # Some fields are read-only

    # Group fields into sections for better organization
    fieldsets = (
        (None, {
            'fields': ('user', 'store', 'total_amount', 'payment_status', 'order_status')
        }),
        ('Address Information', {
            'fields': ('street_address', 'city', 'state', 'pin_code', 'country')
        }),
        ('Tracking Information', {
            'fields': ('tracking_id', 'delivery_status')
        }),
        ('Timestamps', {
            'fields': ('placed_at', 'updated_at')
        }),
    )

    # Add Payment and OrderItem as inline views
    inlines = [OrderItemInline, PaymentInline]












class EcommerceAdminSite(admin.AdminSite):
    site_header = "E-commerce Dashboard"
    site_title = "E-commerce Admin"

    def get_urls(self):
        # Get the default admin URLs
        urls = super().get_urls()
        # Add our custom report view to the URLs
        custom_urls = [
            path('reports/', self.admin_view(self.reports_view), name='ecommerce_reports'),
        ]
        return custom_urls + urls

    # Define the reports view
    def reports_view(self, request):
        # Total sales
        total_sales = Order.objects.filter(payment_status='Completed').aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0

        # Sales per store
        sales_per_store = Order.objects.filter(payment_status='Completed').values('store__name').annotate(store_sales=Sum('total_amount'))

        # Most popular products
        popular_products = OrderItem.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]

        # Pass the data to the template
        context = {
            'total_sales': total_sales,
            'sales_per_store': sales_per_store,
            'popular_products': popular_products,
        }
        return render(request, 'admin/ecommerce_reports.html', context)

# Register the custom admin site
ecommerce_admin_site = EcommerceAdminSite(name='ecommerce_admin')

class ReportsLinkAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # This prevents the model from showing in the changelist
        return False

    # We add a custom change list link to the reports
    def changelist_view(self, request, extra_context=None):
        return self.admin_site.reports_view(request)

# Register the Reports link so it appears in the Application section of the admin
# admin.site.register(Store, ReportsLinkAdmin)
# admin.site.register(EcommerceAdminSite)
# Register the Order model in the admin
admin.site.register(Order, OrderAdmin)

# Register both models in the admin
admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductImage)
# Register both models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
# Register both models
admin.site.register(Attribute, AttributeAdmin)
# admin.site.register(AttributeValue)
admin.site.register(Store, StoreAdmin)


# Register the admin with the custom CouponAdmin
admin.site.register(Coupon, CouponAdmin)


# Register the modified UserAdmin
admin.site.register(User, CustomUserAdmin)
# Define a custom UserAdmin for displaying customer-centric information


# admin.site.register(Product, ProductAdmin)

