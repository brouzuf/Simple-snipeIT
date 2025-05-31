from django.db import models
from django.utils.translation import gettext_lazy as _

class AssetCategoryConfiguration(models.Model):
    MODE_CHOICES = [
        ('select', _('Display category selector')),
        ('fixed', _('Use fixed list of categories')),
    ]

    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default='select',
        verbose_name=_('Assignment Category Mode'),
        help_text=_("Determines if users select a category during assignment, or if a fixed list (defined below) is used.")
    )
    allowed_category_ids = models.JSONField(
        default=list,
        blank=True, # Allows empty list if mode is 'select' or if no categories are fixed yet.
        verbose_name=_('Allowed Asset Category IDs'),
        help_text=_("List of Snipe-IT category IDs. Used when mode is 'fixed'. The asset's actual category must be in this list.")
    )

    class Meta:
        verbose_name = _('Asset Category Configuration')
        verbose_name_plural = _('Asset Category Configurations') # Typically, only one instance will exist.

    def __str__(self):
        return f"Asset Category Assignment Configuration ({self.get_mode_display()})"

    @classmethod
    def get_solo(cls):
        """
        Retrieves the singleton instance of this configuration model.
        Creates it if it doesn't exist, ensuring it always uses pk=1.
        """
        # Try to get the object with pk=1
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'mode': 'select', # Sensible default for mode
            'allowed_category_ids': [] # Sensible default for allowed_category_ids
        })
        # If it was just created, it will have pk=1.
        # If it already existed and somehow had a different pk (should not happen with the save method override),
        # this pattern would create a new one with pk=1.
        # However, the save() method override is the primary guard for pk=1.
        return obj

    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure that this model instance always has pk=1,
        making it a singleton.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls): # Alias for convenience and clearer intent in views
        """
        Convenience alias for get_solo() to load the configuration.
        """
        return cls.get_solo()

# Example of how this might be used in a view (conceptual):
# from .models import AssetCategoryConfiguration
# config = AssetCategoryConfiguration.load()
# current_mode = config.mode
# allowed_ids = config.allowed_category_ids
#
# To save changes:
# config.mode = 'fixed'
# config.allowed_category_ids = [1, 2, 3]
# config.save()
