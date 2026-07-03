from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('knowmore/', views.knowmore, name='knowmore'),
    path('places/', views.places, name='places'),
    path('contact/', views.contact_view, name='contact'),
    path('book-hotel/', views.book_hotel, name='book_hotel'),
    path('hotels/<int:id>/', views.hotel_detail, name='hotel_detail'),
    path("booking/start/<int:hotel_id>/", views.start_booking, name="start_booking"),
    path("booking/summary/<int:booking_id>/", views.booking_summary, name="booking_summary"),
    path("booking/invoice/<int:booking_id>/", views.booking_invoice_pdf, name="booking_invoice_pdf"),
    path("places/portblair/", views.portblair, name="portblair"),
    path("places/cellularjail/", views.cellularjail, name="cellularjail"),
    path("places/rossisland/", views.rossisland, name="rossisland"),
    path("places/havelock/", views.havelock, name="havelock"),
    path("places/barren/", views.barren, name="barren"),
    path("places/neil/", views.neil, name="neil"),
    path("places/sawmill/", views.sawmill, name="sawmill"),
    path("places/limestone-cave/", views.limestone_cave, name="limestone_cave"),
    path("places/mud-volcano/", views.mud_volcano, name="mud_volcano"),
    path("places/flagpoint/", views.flagpoint, name="flagpoint"),
    path("places/indirapoint/", views.indirapoint, name="indirapoint"),
    path("places/parrot-island/", views.parrot_island, name="parrot_island"),
    path("packages/", views.package_list, name="package_list"),
    path("packages/<int:pk>/", views.package_detail, name="package_detail"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("package/<int:pk>/book/", views.book_package, name="book_package"),





]
