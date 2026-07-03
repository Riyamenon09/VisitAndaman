from django.test import TestCase

# Create your tests here.
# python manage.py shell
from main.models import Hotel, HotelImage
h = Hotel.objects.get(id=2)
h.gallery.count(), list(h.gallery.values_list('id','image'))
