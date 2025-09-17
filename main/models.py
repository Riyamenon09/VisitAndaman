from django.db import models

# Create your models here.
# main/models.py
from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='places/')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'PLACES'  # 👈 This will set the table name to PLACES
# main/models.py
from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # Optional long text
    rating = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    # room_type = models.CharField(max_length=20)  # single, double, suite
    sea_view = models.BooleanField(default=False)
    free_wifi = models.BooleanField(default=False)
    parking_available = models.BooleanField(default=False)
    has_spa = models.BooleanField(default=False)
    swimming_pool = models.BooleanField(default=False)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)  
    address = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        db_table = 'HOTELS'

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    arrival_date = models.DateField(blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.email}"
    class Meta:
        db_table = 'CONTACTMESSAGE'
class HotelImage(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='hotel_gallery/')

    def __str__(self):
        return f"Image for {self.hotel.name}"
    class Meta:
        db_table = 'HOTELIMAGE'

class HotelDetail(models.Model):
    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE, related_name='detail')

    # long texts
    highlights = models.TextField(blank=True, null=True)           # comma/newline separated
    amenities = models.TextField(blank=True, null=True)            # comma/newline separated
    about = models.TextField(blank=True, null=True)
    location_description = models.TextField(blank=True, null=True)
    map_embed_url = models.CharField(max_length=200, blank=True, null=True)

    # scores (0.0–10.0 style, DECIMAL(3,1) matches your MySQL)
    cleanliness_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    facilities_score   = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    location_score     = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    review_score       = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # overall
    service_score      = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    total_reviews      = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Details for {self.hotel.name}"
class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')

    # stay
    check_in = models.DateField()
    check_out = models.DateField()
    rooms = models.PositiveIntegerField(default=1)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    child_ages_csv = models.CharField(max_length=100, blank=True, default="")  # e.g. "5,12"

    # lead guest
    first_name = models.CharField(max_length=80)
    last_name  = models.CharField(max_length=80)
    email      = models.EmailField()
    phone      = models.CharField(max_length=30, blank=True)

    # default country (not shown in form)
    country = models.CharField(max_length=60, default="India")

    # preferences
    pref_smoking = models.CharField(
        max_length=12, choices=[('non', 'Non‑smoking'), ('smoking', 'Smoking')], blank=True
    )
    pref_bed = models.CharField(
        max_length=12, choices=[('large', 'Large bed'), ('twin', 'Twin beds')], blank=True
    )
    extra_requests = models.TextField(blank=True)

    # price
    computed_total = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} @ {self.hotel.name} ({self.check_in} → {self.check_out})"
# tour/models.py
from django.db import models

# models.py
from django.db import models

# models.py
from django.db import models
from django.db import models

class Package(models.Model):
    REGION_CHOICES = [
        ("north", "North Andaman"),
        ("south", "South Andaman"),
        ("middle", "Middle Andaman"),
        ("little", "Little Andaman"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    highlights = models.TextField(blank=True, null=True)
    inclusions = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    place = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="south")
    main_image = models.ImageField(upload_to="package/")

    # NEW FIELDS
    accommodation_info = models.TextField(blank=True, null=True)   # Hotel details
    transfers_meals = models.TextField(blank=True, null=True)      # Transfer/Meals info
    customer_reviews = models.TextField(blank=True, null=True)     # Reviews (multi-line)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)  # Rating stars
    map_embed = models.TextField(blank=True, null=True)            # Google Maps embed URL

    def __str__(self):
        return self.title


class PackageImage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="package/gallery/")

    def __str__(self):
        return f"Image for {self.package.title}"


class PackageDay(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="days")
    day_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        ordering = ["day_number"]

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"
from django.db import models

from django.db import models

class ChatPlace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = 'chatplace'   # 👈 tell Django to use your manual table
        managed = False  

    def __str__(self):
        return self.name

class PackageBooking(models.Model):
    package = models.ForeignKey("Package", on_delete=models.CASCADE, related_name="package_bookings")

    # Guest details
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Stay info
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    child_ages_csv = models.CharField(max_length=100, blank=True, default="")

    # Extra info
    health_issues = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(
        max_length=20,
        choices=[
            ("upi", "UPI"),
            ("card", "Credit/Debit Card"),
            ("netbanking", "Net Banking"),
            ("cod", "Cash on Arrival"),
        ],
        default="upi"
    )

    # Pricing
    computed_total = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.package.title}"
    class Meta:
        db_table = "packagebooking"
