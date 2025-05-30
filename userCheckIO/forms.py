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
                                      'autofocus': 'autofocus',
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
    asset_tag = forms.CharField(
        label="Asset Tag",
        required=True,
        max_length=100, # Assuming a reasonable max length for asset tags
        widget=forms.TextInput(attrs={'class': 'input',
                                      'autofocus': 'autofocus',
                                      'placeholder': _('Enter asset tag to assign')}) # Corrected placeholder
    )

class UnassignAssetForm(forms.Form):
    asset_tag = forms.CharField(
        label=_("Asset Tag to Unassign"), # Using gettext_lazy for potential translation
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input',
                                      'autofocus': 'autofocus',
                                      'placeholder': _('Enter asset tag to unassign')})
    )

class CategoryConfigForm(forms.Form):
    allowed_categories = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False, # An empty list is allowed
        label=_("Featured Asset Categories"),
        help_text=_("Select categories to be highlighted in special reports or views. An empty selection is valid.")
    )

    def __init__(self, *args, **kwargs):
        categories_choices = kwargs.pop('categories_choices', None)
        super().__init__(*args, **kwargs)
        if categories_choices:
            self.fields['allowed_categories'].choices = categories_choices
        else:
            self.fields['allowed_categories'].choices = [('', 'No categories available to configure')]

        # Dynamically set required based on mode; this is tricky for initial load
        # and might be better handled in view validation or with JavaScript.
        # For now, 'required=False' on field and view will validate.
        # if self.initial.get('mode') == 'fixed' or (self.is_bound and self.data.get('mode') == 'fixed'):
        #     self.fields['allowed_categories'].required = True
