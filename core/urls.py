# -*- encoding: utf-8 -*-


from django.contrib import admin
from django.urls import include, path  # add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("authentication.urls")),  # add this
    path("", include("app.urls")), # add this
    path("accounts/", include("allauth.urls"))
    # path("", include("googleauthnetication.urls"))
]
