from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Property, CustomUser
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.conf import settings
from django.core.mail import send_mail


def send_email(email_body, subject, email):
    send_mail(
        subject,
        email_body,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def index(request):
    return render(request, 'home/home.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('list')
    if request.method == 'POST':
        username_email = request.POST.get('username_email')
        password = request.POST.get('password')
        username = ""
        if CustomUser.objects.filter(username=username_email).exists():
            user = CustomUser.objects.filter(username=username_email).first()
            username = user.username
        if CustomUser.objects.filter(email=username_email).exists():
            user = CustomUser.objects.filter(email=username_email).first()
            username = user.username
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list')
        else:
            if not CustomUser.objects.filter(username=username_email).exists() and not CustomUser.objects.filter(email=username_email).exists():
                messages = "User does not exist"
            else:
                messages = "Invalid password"
            return render(request, 'home/login.html', {'message': messages})
    return render(request, 'home/login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('list')
    if request.method == 'POST':
        username = request.POST.get('email').split('@')[0]
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        data = {
            "username": username,
            "password": password,
            "email": email,
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
        }
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'home/register.html', {'message': 'Username already exists.', 'data': data})

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'home/register.html', {'message': 'Email already exists.', 'data': data})
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone Number already exists.')
            return render(request, 'home/register.html', {'message': 'Phone Number already exists.', 'data': data})

        user = CustomUser.objects.create_user(username=username, password=password, email=email, phone_number=phone_number, first_name=first_name,
                                              last_name=last_name,
                                              is_registered=True)
        login(request, user)
        return redirect('list')
    else:
        message = request.GET.get('message')
        return render(request, 'home/register.html', {'message': message})


def user_logout(request):
    logout(request)
    return redirect('home_index')


@login_required
def user_dashboard(request):
    user_posts = Property.objects.filter(
        owner=request.user).order_by('-updated_at')
    context = {
        'user': request.user,
        'posts': user_posts
    }
    return render(request, 'home/user_dashboard.html', context)


@login_required
def user_detail(request, username):
    user = get_object_or_404(CustomUser, username=username)
    user_posts = Property.objects.filter(owner=user).order_by('-created_at')
    context = {
        'user': user,
        'posts': user_posts
    }
    return render(request, 'home/user_detail.html', context)


@login_required
def update_user_details(request):

    if request.method == 'POST':
        user = request.user
        username = user.username
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        data = {
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'first_name': first_name,
            'last_name': last_name,
            'city': city,
            'country': country,

        }
        if phone_number != user.phone_number and CustomUser.objects.filter(phone_number=phone_number).exclude(username=user.username).exists():
            messages.error(request, 'Phone number already exists.')
            return render(request, 'home/update.html', {'message': 'Phone number already exists.', 'data': data})
        if email != user.email and CustomUser.objects.filter(email=email).exists():
            return render(request, 'home/update.html', {'message': 'Email already exists.', 'data': data})

        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.first_name = first_name
        user.last_name = last_name
        user.city = city
        user.country = country
        user.save()

        messages.success(
            request, 'Your details have been updated successfully.')
        return redirect('user_dashboard')
    else:
        return render(request, 'home/update.html', {'data': request.user})


@login_required
def list(request):
    property_list = Property.objects.all().order_by('-updated_at')
    query = request.GET.get('q')
    if query:
        property_list = property_list.filter(
            Q(place__icontains=query) |
            Q(description__icontains=query)
        )

    # Handle filtering
    place = request.GET.get('place')
    if place:
        property_list = property_list.filter(place__icontains=place)

    area_min = request.GET.get('area_min')
    if area_min:
        property_list = property_list.filter(area__gte=float(area_min))

    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        property_list = property_list.filter(bedrooms=int(bedrooms))

    bathrooms = request.GET.get('bathrooms')
    if bathrooms:
        property_list = property_list.filter(bathrooms=int(bathrooms))

    nearby_hospitals = request.GET.get('nearby_hospitals')
    if nearby_hospitals:
        property_list = property_list.filter(
            nearby_hospitals__icontains=nearby_hospitals)

    nearby_colleges = request.GET.get('nearby_colleges')
    if nearby_colleges:
        property_list = property_list.filter(
            nearby_colleges__icontains=nearby_colleges)

    paginator = Paginator(property_list, 5)  # Show 5 properties per page

    page_number = request.GET.get('page')
    try:
        properties = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        properties = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        properties = paginator.page(paginator.num_pages)

    return render(request, 'home/list.html', {'properties': properties})


@login_required
def like_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    if property.likes.filter(id=request.user.id).exists():
        property.likes.remove(request.user)
        liked = False
    else:
        property.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': property.total_likes()})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Property, id=post_id, owner=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted successfully.')
    return redirect('user_dashboard') 

@login_required
def edit_property(request, post_id):
    post = get_object_or_404(Property, id=post_id, owner=request.user)
    if request.method == 'POST':
        # Ensure the user owns the property before allowing edit
        if post.owner == request.user:
            # Retrieve data from the form
            post.title = request.POST.get('title')
            post.description = request.POST.get('description')
            post.place = request.POST.get('place')
            post.area = float(request.POST.get('area'))
            post.bedrooms = int(request.POST.get('bedrooms'))
            post.bathrooms = int(request.POST.get('bathrooms'))
            post.nearby_hospitals = request.POST.get('nearby_hospitals')
            post.nearby_colleges = request.POST.get('nearby_colleges')
            post.image = request.FILES.get('image')

            try:
                post.save()
                messages.success(
                    request, 'Your details have been updated successfully.')
                return redirect('user_dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
                return redirect('edit_property', post_id=post_id)
        else:
            messages.error(
                request, 'You are not authorized to edit this property.')
            return redirect('user_dashboard')
    return render(request, 'home/edit_property.html', {'post': post})


@login_required
def add_property(request):
    if request.method == 'POST':
        owner = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        place = request.POST.get('place')
        area = request.POST.get('area').replace("e", '')
        bedrooms = request.POST.get('bedrooms').replace("e", '')
        bathrooms = request.POST.get('bathrooms').replace("e", '')
        nearby_hospitals = request.POST.get('nearby_hospitals')
        nearby_colleges = request.POST.get('nearby_colleges')
        image = request.FILES.get('image')

        property_obj = Property.objects.create(
            owner=owner,
            title=title,
            description=description,
            place=place,
            area=area,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            nearby_hospitals=nearby_hospitals,
            nearby_colleges=nearby_colleges,
            image=image,
        )

        return redirect('user_dashboard')

    return render(request, 'home/add_property.html')


@login_required
def express_interest(request, property_id):
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    property = get_object_or_404(Property, id=property_id)
    user = request.user
    email_body = f"""
    User {user.username} | {user.email},{
    user.phone_number} is interested in your property {property.title}.
    """
    subject = "Interest in Your Property"
    email = property.owner.email
    send_email(email_body, subject, email)

    email_body = f"""
Dear {user.username},

I hope this email finds you well. I am pleased to provide you with the details of the property you are interested in. Please find the comprehensive information below:

Owner Details:
Name: {property.owner.first_name} {property.owner.last_name}
Contact Details: {property.owner.email}
Profile Link: {protocol}://{domain}/user/{property.owner.username}/
Title: {property.title}
Property Details:

Location: {property.place}
Area:{property.area} square feet
Description: {property.description}

Specifications:
Bedrooms: {property.bedrooms}
Bathrooms: {property.bathrooms}

Nearby Amenities:
Hospitals: {property.nearby_hospitals}
Colleges: {property.nearby_colleges}

If you have any questions or need further information, please do not hesitate to contact me. I am here to assist you throughout the buying process and ensure you have all the information you need to make an informed decision.

Thank you for your interest in this property. I look forward to hearing from you soon.
"""
    subject = "Property Details for Your Consideration"
    email = user.email
    send_email(email_body, subject, email)

    messages.success(request, 'Your message has been sent to the owner.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))
