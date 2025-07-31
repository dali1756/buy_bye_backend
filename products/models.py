from django.db import models

class MainCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    main_category = models.ForeignKey("MainCategory", on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    main_category = models.ForeignKey("MainCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    sub_category = models.ForeignKey("SubCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

Category = MainCategory
