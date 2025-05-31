from django.contrib import admin
from .models import AssetCategoryConfiguration

@admin.register(AssetCategoryConfiguration)
class AssetCategoryConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'mode', 'display_allowed_category_ids')
    # fields = ('mode', 'allowed_category_ids') # To control field order in edit view if needed

    def display_allowed_category_ids(self, obj):
        # More friendly display for the JSONField list
        ids = obj.allowed_category_ids
        if isinstance(ids, list):
            return ", ".join(map(str, ids)) if ids else "None"
        return ids # Should be a list, but fallback
    display_allowed_category_ids.short_description = 'Allowed Category IDs'

    def has_add_permission(self, request):
        # Disable 'Add' button as this is a singleton.
        # The object is created by AssetCategoryConfiguration.load() or .get_solo() if it doesn't exist.
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable 'Delete' action as this is a singleton.
        return False

    def get_queryset(self, request):
        # Ensure that even if somehow multiple objects were created (e.g. before singleton logic was perfect),
        # only the one with pk=1 is shown.
        qs = super().get_queryset(request)
        # Attempt to load the singleton instance to create it if it doesn't exist yet,
        # so it appears in the admin for editing immediately after first app setup.
        AssetCategoryConfiguration.load()
        return qs.filter(pk=1)

# Note: To ensure the admin interface shows the single configuration object
# immediately after running migrations (even before it's accessed by the app),
# you might consider adding a signal in apps.py or a management command
# to call AssetCategoryConfiguration.load() once.
# However, the get_queryset modification above will also effectively make it available
# for editing as soon as the admin page is visited.
