"""ride_share URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls), #将url pattern关联到view
    path('myapp/', include('myapp.urls')),
    path('', RedirectView.as_view(url='/myapp/')), #redirect /myapp
]

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('myapp/', include('myapp.urls')),
]

# Use include() to add URLS from the myapp application and authentication system
from django.urls import include
#

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('', include('django.contrib.auth.urls')),
]