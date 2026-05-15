from django.db import models
from django.contrib.auth.models import User # This handles our logins

class Donation(models.Model):
    # Link the donation to a specific user (the donor)
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    food_name = models.CharField(max_length=100)
    quantity = models.FloatField() # In kg or units
    food_image = models.ImageField(upload_to='food_images/')
    # We will use these for the location feature later
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Automatically records when the food was posted
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Track if the food is still available
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.food_name} - {self.quantity}"