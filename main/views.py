from django.shortcuts import render, redirect, get_object_or_404
from .models import Place  # Import your model
from .models import ContactMessage
from django.utils.dateparse import parse_date
from django.contrib import messages
from .models import Hotel
from datetime import date
from .models import Hotel, Booking

def home(request):
    return render(request, 'home.html')
def knowmore(request):
    return render(request, 'knowmore.html')
# tour/views.py
from django.shortcuts import render
from .models import Package
# views.py
from django.shortcuts import render, get_object_or_404
from .models import Package

def package_detail(request, pk):
    package = get_object_or_404(Package, pk=pk)
    return render(request, "package_detail.html", {"package": package})

# views.py
def package_list(request):
    packages = Package.objects.all()

    # filters
    price_filter = request.GET.get("price")
    place_filter = request.GET.get("place")
    guide_filter = request.GET.get("guide")
    region_filter = request.GET.get("region")

    if price_filter == "low":
        packages = packages.filter(price__lt=20000)
    elif price_filter == "mid":
        packages = packages.filter(price__gte=20000, price__lte=40000)
    elif price_filter == "high":
        packages = packages.filter(price__gt=40000)

    if place_filter and place_filter != "all":
        packages = packages.filter(place__iexact=place_filter)

    if guide_filter and guide_filter != "all":
        packages = packages.filter(guide_gender=guide_filter)

    if region_filter and region_filter != "all":
        packages = packages.filter(region=region_filter)

    return render(request, "package.html", {"packages": packages})
def package_detail(request, pk):
    package = get_object_or_404(Package, pk=pk)
    days = package.days.order_by("day_number")   # fetch day plan
    return render(request, "package_detail.html", {"package": package, "days": days})


def places(request):
    places = Place.objects.all()  # Fetch all places from the database
    return render(request, 'places.html', {'places': places})
from django.shortcuts import render
from .models import Hotel

def book_hotel(request):
    hotels = Hotel.objects.all()

    rating = request.GET.get('rating')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    room_type = request.GET.get('room_type')
    sea_view = request.GET.get('sea_view')

    if rating:
        hotels = hotels.filter(rating__gte=rating)
    if min_price:
        hotels = hotels.filter(price_per_night__gte=min_price)
    if max_price:
        hotels = hotels.filter(price_per_night__lte=max_price)
    if room_type:
        hotels = hotels.filter(room_type=room_type)
    if sea_view:
        hotels = hotels.filter(sea_view=True)

    return render(request, 'book_hotel.html', {'hotels': hotels})
def _split_items(text):
    if not text:
        return []
    # allow either comma or newline separated
    raw = [p.strip() for p in text.replace("\r", "").replace("•", "").split("\n")]
    parts = []
    for line in raw:
        if not line:
            continue
        parts.extend([x.strip() for x in line.split(",") if x.strip()])
    # dedupe while preserving order
    seen, out = set(), []
    for x in parts:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

# def hotel_detail(request, pk):
#     hotel = get_object_or_404(Hotel.objects.select_related("detail").prefetch_related("gallery"), pk=pk)
#     id=id
#     detail = getattr(hotel, "detail", None)

#     context = {
#         "hotel": hotel,
#         "today": date.today(),
#         "highlights_list": _split_items(detail.highlights) if detail else [],
#         "amenities_list": _split_items(detail.amenities) if detail else [],

#         # scores (use None-safe defaults)
#         "review_score": getattr(detail, "review_score", None),
#         "total_reviews": getattr(detail, "total_reviews", None),
#         "location_score": getattr(detail, "location_score", None),

#         # category chips:
#         "category_scores": {
#             "Location": getattr(detail, "location_score", None),
#             "Service": getattr(detail, "service_score", None),
#             "Cleanliness": getattr(detail, "cleanliness_score", None),
#             "Facilities": getattr(detail, "facilities_score", None),
#         } if detail else {},
#     }
#     return render(request, "hotel_detail.html", context)
# main/views.py  (or wherever your view lives)
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseBadRequest
from .models import Hotel  # adjust import to your app structure

def hotel_detail(request, id):
    hotel = get_object_or_404(Hotel, pk=id)

    # If you have a related detail object / highlights / amenities already split:
    detail = getattr(hotel, "detail", None)

    highlights = []
    amenities = []
    if detail and detail.highlights:
        # supports comma/newline separated strings
        highlights = [h.strip() for h in detail.highlights.replace("\r", "\n").split("\n") if h.strip()]
        if not highlights and "," in detail.highlights:
            highlights = [h.strip() for h in detail.highlights.split(",") if h.strip()]

    if detail and detail.amenities:
        amenities = [a.strip() for a in detail.amenities.replace("\r", "\n").split("\n") if a.strip()]
        if not amenities and "," in detail.amenities:
            amenities = [a.strip() for a in detail.amenities.split(",") if a.strip()]

    # Example “scores” structure if you store sub-scores
    scores = []
    if detail:
        for label, val in [
            ("Cleanliness", getattr(detail, "cleanliness_score", None)),
            ("Comfort",     getattr(detail, "comfort_score", None)),
            ("Location",    getattr(detail, "location_score", None)),
            ("Facilities",  getattr(detail, "facilities_score", None)),
        ]:
            if val is not None:
                pct = max(0, min(100, int((float(val)/10.0)*100)))
                scores.append({"label": label, "value": f"{val}/10", "pct": pct})

    context = {
        "hotel": hotel,
        "detail": detail,
        "highlights": highlights,
        "amenities": amenities,
        "scores": scores,
        "today": timezone.localdate(),  # for min date in template
    }
    return render(request, "hotel_detail.html", context)


def compute_total_price(base_price, check_in, check_out, rooms, adults, children, child_ages):
    """
    Pricing rule (match front-end):
      - Nights = max(1, (check_out - check_in).days)
      - Base per night = base_price * rooms
      - Guest factor = adults*1.0 + sum(child<10 ? 0.5 : 1.0)
      - Total = base_per_night * nights * guest_factor
    """
    nights = (check_out - check_in).days
    if nights <= 0:
        nights = 1

    base_per_night = base_price * rooms

    child_weight = 0.0
    for age in child_ages:
        try:
            a = int(age)
        except:
            a = 0
        child_weight += 0.5 if a < 10 else 1.0

    guest_factor = max(1.0, float(adults) + child_weight)
    total = base_per_night * nights * guest_factor

    # round to nearest rupee
    return round(total)


# def start_booking(request, hotel_id):
#     hotel = get_object_or_404(Hotel, pk=hotel_id)

#     # Parse inputs
#     ci = request.GET.get("check_in")
#     co = request.GET.get("check_out")
#     rooms = int(request.GET.get("rooms", "1"))
#     adults = int(request.GET.get("adults", "1"))
#     children = int(request.GET.get("children", "0"))
#     child_ages_raw = request.GET.get("child_ages", "")

#     # Basic validation
#     if not ci or not co:
#         return HttpResponseBadRequest("Missing dates")

#     try:
#         check_in = datetime.strptime(ci, "%Y-%m-%d").date()
#         check_out = datetime.strptime(co, "%Y-%m-%d").date()
#     except ValueError:
#         return HttpResponseBadRequest("Invalid date format")

#     # Process child ages list
#     child_ages = [x for x in child_ages_raw.split(",") if x != ""]
#     # If user said children=n but didn't send ages, default to 0
#     if len(child_ages) < children:
#         child_ages += ["0"] * (children - len(child_ages))
#     child_ages = child_ages[:children]

#     # Server-side recompute for safety
#     base = float(hotel.price_per_night)
#     total = compute_total_price(
#         base_price=base,
#         check_in=check_in,
#         check_out=check_out,
#         rooms=max(1, rooms),
#         adults=max(0, adults),
#         children=max(0, children),
#         child_ages=child_ages
#     )

#     nights = (check_out - check_in).days
#     if nights <= 0:
#         nights = 1

#     context = {
#         "hotel": hotel,
#         "check_in": check_in,
#         "check_out": check_out,
#         "nights": nights,
#         "rooms": rooms,
#         "adults": adults,
#         "children": children,
#         "child_ages": child_ages,
#         "computed_total": total,
#     }
#     return render(request, "start_booking.html", context)
# main/views.py
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from .models import Hotel, Booking

# main/views.py
from datetime import datetime
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

from .models import Hotel, Booking

def compute_total_price(base_price, check_in, check_out, rooms, adults, children, child_ages):
    nights = (check_out - check_in).days
    if nights <= 0:
        nights = 1
    base_per_night = float(base_price) * rooms
    child_weight = sum(0.5 if int(age) < 10 else 1.0 for age in child_ages if age != "")
    guest_factor = max(1.0, float(adults) + child_weight)
    total = base_per_night * nights * guest_factor
    return round(total)


def hotel_detail(request, id):
    hotel = get_object_or_404(
        Hotel.objects.select_related("detail").prefetch_related("gallery"),
        pk=id
    )

    detail = getattr(hotel, "detail", None)

    def _split(txt):
        if not txt: return []
        parts = [p.strip() for p in txt.replace("\r","\n").split("\n") if p.strip()]
        if not parts and "," in txt:
            parts = [p.strip() for p in txt.split(",") if p.strip()]
        return parts

    highlights = _split(getattr(detail, "highlights", ""))
    amenities  = _split(getattr(detail, "amenities", ""))

    scores = []
    if detail:
        for label, val in [
            ("Cleanliness", getattr(detail, "cleanliness_score", None)),
            ("Comfort",     getattr(detail, "comfort_score", None)),
            ("Location",    getattr(detail, "location_score", None)),
            ("Facilities",  getattr(detail, "facilities_score", None)),
        ]:
            if val is not None:
                pct = max(0, min(100, int((float(val)/10)*100)))
                scores.append({"label": label, "value": f"{val}/10", "pct": pct})

    return render(request, "hotel_detail.html", {
        "hotel": hotel,
        "detail": detail,
        "highlights": highlights,
        "amenities": amenities,
        "scores": scores,
        "today": timezone.localdate(),
    })

# from main.models import Hotel, HotelImage
# h = Hotel.objects.get(id=2)
# print("hi")
# print(h.gallery.count(), list(h.gallery.values_list("image", flat=True)))
def start_booking(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)

    # read selections (GET first visit, POST on submit)
    if request.method == "GET":
        ci = request.GET.get("check_in")
        co = request.GET.get("check_out")
        rooms = int(request.GET.get("rooms", "1"))
        adults = int(request.GET.get("adults", "1"))
        children = int(request.GET.get("children", "0"))
        child_ages_raw = request.GET.get("child_ages", "")
    else:
        ci = request.POST.get("check_in")
        co = request.POST.get("check_out")
        rooms = int(request.POST.get("rooms", "1"))
        adults = int(request.POST.get("adults", "1"))
        children = int(request.POST.get("children", "0"))
        child_ages_raw = request.POST.get("child_ages", "")

    if not ci or not co:
        return HttpResponseBadRequest("Missing dates")

    try:
        check_in = datetime.strptime(ci, "%Y-%m-%d").date()
        check_out = datetime.strptime(co, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date format")

    child_ages = [x for x in child_ages_raw.split(",") if x != ""]
    if len(child_ages) < children:
        child_ages += ["0"] * (children - len(child_ages))
    child_ages = child_ages[:children]

    total = compute_total_price(
        base_price=hotel.price_per_night,
        check_in=check_in, check_out=check_out,
        rooms=rooms, adults=adults, children=children, child_ages=child_ages
    )
    nights = (check_out - check_in).days or 1

    if request.method == "POST":
        # Required fields
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        email      = request.POST.get("email", "").strip()
        phone      = request.POST.get("phone", "").strip()
        pref_smoking   = request.POST.get("pref_smoking", "")
        pref_bed       = request.POST.get("pref_bed", "")
        extra_requests = request.POST.get("extra_requests", "")

        if not first_name or not last_name or not email or not phone:
            error_msg = "Please fill all required fields."
            return render(request, "start_booking.html", {
                "hotel": hotel, "check_in": check_in, "check_out": check_out, "nights": nights,
                "rooms": rooms, "adults": adults, "children": children, "child_ages": child_ages,
                "computed_total": total, "error_msg": error_msg
            })

        booking = Booking.objects.create(
            hotel=hotel,
            check_in=check_in, check_out=check_out,
            rooms=rooms, adults=adults, children=children,
            child_ages_csv=",".join(child_ages),
            first_name=first_name, last_name=last_name,
            email=email, phone=phone, country="India",
            pref_smoking=pref_smoking, pref_bed=pref_bed,
            extra_requests=extra_requests,
            computed_total=total
        )
        messages.success(request, "Thank you! Your details were submitted successfully.")
        return redirect(reverse("booking_summary", args=[booking.id]))

    return render(request, "start_booking.html", {
        "hotel": hotel, "check_in": check_in, "check_out": check_out, "nights": nights,
        "rooms": rooms, "adults": adults, "children": children, "child_ages": child_ages,
        "computed_total": total,
    })

def booking_summary(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "booking_summary.html", {"booking": booking})

def booking_invoice_pdf(request, booking_id):
    """
    Generates a simple PDF invoice using reportlab.
    pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
    except ImportError:
        return HttpResponse("Install reportlab: pip install reportlab", status=500)

    booking = get_object_or_404(Booking, pk=booking_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 30*mm
    p.setFont("Helvetica-Bold", 16)
    p.drawString(25*mm, y, "Hotel Booking Invoice")
    y -= 12*mm

    p.setFont("Helvetica", 11)
    p.drawString(25*mm, y, f"Booking ID: {booking.id}")
    y -= 7*mm
    p.drawString(25*mm, y, f"Hotel: {booking.hotel.name}")
    y -= 7*mm
    p.drawString(25*mm, y, f"Guest: {booking.first_name} {booking.last_name}")
    y -= 7*mm
    p.drawString(25*mm, y, f"Email: {booking.email}  |  Phone: {booking.phone}")
    y -= 7*mm
    p.drawString(25*mm, y, f"Stay: {booking.check_in} → {booking.check_out}")
    y -= 7*mm
    p.drawString(25*mm, y, f"Rooms: {booking.rooms}  Adults: {booking.adults}  Children: {booking.children} ({booking.child_ages_csv})")
    y -= 10*mm

    p.setFont("Helvetica-Bold", 12)
    p.drawString(25*mm, y, f"Total: ₹{booking.computed_total}")
    y -= 15*mm

    p.setFont("Helvetica", 9)
    p.drawString(25*mm, y, "Thank you for choosing us! This is a computer-generated invoice.")
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{booking.id}.pdf"'
    return response

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        arrival_date = request.POST.get('arrival_date')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            phone=phone,
            email=email,
            arrival_date=parse_date(arrival_date) if arrival_date else None,
            message=message
        )

        messages.success(request, 'Thank you! Your message has been received.')
        return redirect('contact')

    return render(request, 'contact.html')
from django.shortcuts import render

def portblair(request):
    return render(request, "places/portblair.html")

def cellularjail(request):
    return render(request, "places/cellularjail.html")

def rossisland(request):
    return render(request, "places/rossisland.html")

def havelock(request):
    return render(request, "places/havelock.html")

def barren(request):
    return render(request, "places/barren.html")

def neil(request):
    return render(request, "places/neil.html")

def sawmill(request):
    return render(request, "places/sawmill.html")

def limestone_cave(request):
    return render(request, "places/limestone_cave.html")

def mud_volcano(request):
    return render(request, "places/mud_volcano.html")

def flagpoint(request):
    return render(request, "places/flagpoint.html")

def indirapoint(request):
    return render(request, "places/indirapoint.html")

def parrot_island(request):
    return render(request, "places/parrot_island.html")
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package   # Package model maps to main_package table
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import requests
from django.http import JsonResponse
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import requests
from django.http import JsonResponse
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package   # your models
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package
import re
import requests
from django.http import JsonResponse
from .models import ChatPlace, Package


# 🔹 Helper: Clean user query before sending to Wikipedia
def clean_query(text):
    stop_phrases = [
        r"\btell me about\b",
        r"\bwhat is\b",
        r"\bwho is\b",
        r"\bexplain\b",
        r"\bdefine\b",
        r"\binformation on\b",
    ]
    q = text.lower()
    for phrase in stop_phrases:
        q = re.sub(phrase, "", q)
    return q.strip().title()  # Capitalize for Wikipedia


def chatbot(request):
    question_raw = request.GET.get("q", "").strip()
    question = question_raw.lower()
    reply = "Sorry, I don’t have that info."

    # 1️⃣ Check in ChatPlace table (places, booking, safety, etc.)
    for entry in ChatPlace.objects.all():
        if entry.name.lower() in question:
            reply = entry.description
            break

    # 2️⃣ Package pricing queries
    if "price" in question or "cost" in question or "package" in question:
        packages = Package.objects.all()[:3]
        if packages:
            reply = "Here are some sample packages:\n"
            for pkg in packages:
                reply += f"- {pkg.title} ({pkg.place}) – ₹{pkg.price}\n"

    # 3️⃣ Hotel queries
    if "5 star" in question and "hotel" in question:
        reply = (
            "Some luxury 5-star hotels in Andaman are: "
            "Taj Exotica Resort & Spa (Havelock), "
            "ITC Fortune Bay Island (Port Blair), "
            "Symphony Samudra (Port Blair)."
        )
    elif "3 star" in question and "hotel" in question:
        reply = (
            "Popular 3-star hotels include Hotel Sentinel (Port Blair), "
            "Peerless Resort (Havelock), and Blue Bird Resort (Neil Island)."
        )

    # 4️⃣ Booking / billing / payment queries
    if "booking" in question or "book" in question:
        reply = (
            "Booking Steps:\n"
            "1. Choose your package or hotel.\n"
            "2. Select dates and number of guests.\n"
            "3. Fill guest details.\n"
            "4. Make payment.\n"
            "5. You’ll receive booking confirmation & e-bill."
        )
    if "bill" in question or "invoice" in question:
        reply = (
            "Your bill (invoice) is generated instantly after successful payment "
            "and will be available for download in your booking summary page."
        )
    if "payment" in question:
        reply = (
            "We support multiple payment methods: Credit/Debit Cards, "
            "Net Banking, UPI, and Wallets."
        )

    # 5️⃣ Fallback → Wikipedia search
    if reply.startswith("Sorry"):
        try:
            headers = {"User-Agent": "AndamanChatbot/1.0 (https://yourwebsite.com)"}

            # Clean query before Wikipedia
            cleaned_query = clean_query(question_raw)
            print("🔎 Cleaned query for Wikipedia:", cleaned_query)  # debug

            # Step 1: Search Wikipedia
            search_api = (
                f"https://en.wikipedia.org/w/api.php?"
                f"action=query&list=search&srsearch={cleaned_query}&format=json"
            )
            search_res = requests.get(search_api, headers=headers, timeout=5).json()

            if "query" in search_res and search_res["query"]["search"]:
                first_title = search_res["query"]["search"][0]["title"].replace(" ", "_")

                # Step 2: Fetch summary
                wiki_api = f"https://en.wikipedia.org/api/rest_v1/page/summary/{first_title}"
                res = requests.get(wiki_api, headers=headers, timeout=5)

                if res.status_code == 200:
                    data = res.json()
                    if "extract" in data:
                        reply = data["extract"]
                    else:
                        reply = f"⚠️ No summary found for '{first_title}'."
                else:
                    reply = f"⚠️ Wikipedia request failed with status {res.status_code}"
            else:
                reply = f"⚠️ No Wikipedia results for '{cleaned_query}'."

        except Exception as e:
            reply = f"⚠️ Wikipedia fetch failed: {e}"

    return JsonResponse({"reply": reply})
from django.shortcuts import render, get_object_or_404
from .models import Package
from django.shortcuts import render, get_object_or_404
from .models import Package, PackageBooking

def book_package(request, pk):
    package = get_object_or_404(Package, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        adults = int(request.POST.get("adults", 1))
        children = int(request.POST.get("children", 0))
        child_ages = request.POST.get("child_ages", "")
        health_issues = request.POST.get("health_issues", "")
        payment_mode = request.POST.get("payment_mode")

        # Pricing logic: child = 50% of adult price
        price_per_adult = float(package.price)
        price_per_child = price_per_adult * 0.5
        total = int((adults * price_per_adult) + (children * price_per_child))

        # ✅ Save into packagebooking table
        booking = PackageBooking.objects.create(
            package=package,
            name=name,
            email=email,
            phone=phone,
            adults=adults,
            children=children,
            child_ages_csv=child_ages,
            health_issues=health_issues,
            payment_mode=payment_mode,
            computed_total=total,
        )

        return render(request, "booking_success.html", {
            "package": package,
            "name": name,
            "total": total,
            "booking": booking,
        })

    return render(request, "book_package.html", {"package": package})


