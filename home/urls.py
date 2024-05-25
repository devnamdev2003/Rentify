from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home_index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('update/', views.update_user_details, name='update_user_details'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('user/<str:username>/', views.user_detail, name='user_detail'),
    path('list/', views.list, name='list'),
    
    path('property/<int:property_id>/like/', views.like_property, name='like_property'),
    path('post/<int:post_id>/edit/', views.edit_property, name='edit_property'),
    path('post/upload/', views.add_property, name='add_property'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('interest/<int:property_id>/', views.express_interest, name='interest'),

]