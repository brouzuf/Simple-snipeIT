from django import forms
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    # Using a generic username field; Snipe-IT might use email or username.
    # For now, this form doesn't directly use these fields to get a token,
    # as we're using a pre-configured token. This form is a placeholder
    # for a more traditional login flow if requirements change.
    # We'll "log in" by verifying the pre-configured token.
    # If a user needs to enter their *own* Snipe-IT username/password
    # or their *own* API token, this form and the view logic would need
    # to be significantly different (e.g. actually POSTing to Snipe-IT's login).
    # For now, we'll just have a "Login" button that triggers the check
    # of the pre-configured token.
    pass # No fields needed for now as we use a pre-configured token.
         # A button in the template will trigger the login.

class EmployeeNumberForm(forms.Form):
    employee_number = forms.CharField(
        label=_('Enter Your Employee Number'),
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input is-large is-primary',
                                      'title': _('Employee Number'),
                                      'size': '20',
                                      'placeholder': 'Employee Number'})
    )

class CategoryFilterForm(forms.Form):
    category_id = forms.ChoiceField(
        label="Filter by Category", 
        required=False, 
        choices=[('', 'All Categories')] # Default initial choice
    )

    def __init__(self, *args, **kwargs):
        categories_choices = kwargs.pop('categories_choices', [])
        super().__init__(*args, **kwargs)
        # Set choices if provided, ensuring 'All Categories' is always an option
        if categories_choices:
            self.fields['category_id'].choices = [('', 'All Categories')] + categories_choices
        # If not, it will retain the default [('', 'All Categories')]

class AssignAssetForm(forms.Form):
    asset_id = forms.ChoiceField(
        label="Select Asset to Assign", 
        required=True, 
        choices=[] # Initial empty choices, to be populated by the view
    )

    def __init__(self, *args, **kwargs):
        assets_choices = kwargs.pop('assets_choices', [])
        super().__init__(*args, **kwargs)
        if assets_choices:
            # Ensure a default, non-selectable first option if choices are available
            self.fields['asset_id'].choices = [('', '-- Select an Asset --')] + assets_choices
            self.fields['asset_id'].widget.attrs.pop('disabled', None) # Ensure not disabled
        else:
            # If no assets are available, show a message and disable the field
            self.fields['asset_id'].choices = [('', 'No available assets found or error fetching assets')]
            self.fields['asset_id'].widget.attrs['disabled'] = True
        
        # Ensure required=True makes sense with potentially disabled field
        # If disabled and no assets, it shouldn't fail form validation if submitted (though button should be disabled too)
        # For now, the view logic should prevent submission if no assets.
        # If the field is disabled, its value won't be submitted anyway.
        # `required=True` is more for when the field is active and has options.
        if not assets_choices:
            self.fields['asset_id'].required = False # Don't require if disabled and no choices
