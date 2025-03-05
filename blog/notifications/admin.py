from django.contrib import admin

# Register your models here.
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "to_new_posts", "to_engaged_posts"]
    list_filter = ["to_new_posts", "to_engaged_posts"]
    search_fields = ["user__username", "user__email"]


admin.site.register(Subscription, SubscriptionAdmin)
