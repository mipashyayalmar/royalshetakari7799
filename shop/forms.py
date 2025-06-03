from django import forms
from .models import Orders

from .models import Table

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'status']  # Fields to display in the form

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = [
            'items_json', 
            'amount', 
            'name', 
            'email', 
            'address', 
            'city', 
            'state', 
            'zip_code', 
            'phone', 
            'payment_method',  # Add payment_method field
            'payment_comments'  # Add payment_comments field
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply widget customization for all fields
        self.fields['items_json'].widget.attrs.update({'class': 'form-control', 'id': 'items_json'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['zip_code'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        
        # Add form customization for payment_method
        self.fields['payment_method'].widget.attrs.update({'class': 'form-control'})
        
        # Hide the payment_comments field by default
        if self.instance and self.instance.payment_method != 'other':
            self.fields['payment_comments'].widget.attrs.update({'class': 'form-control', 'style': 'display:none;'})
        else:
            self.fields['payment_comments'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        payment_comments = cleaned_data.get('payment_comments')

        # Validate that payment_comments is provided if payment_method is 'other'
        if payment_method == 'other' and not payment_comments:
            self.add_error('payment_comments', "This field is required when 'Other' payment method is selected.")

        return cleaned_data


from django import forms
from .models import Advertise

class AdvertiseForm(forms.ModelForm):
    class Meta:
        model = Advertise
        fields = ['name', 'image2']




from django import forms
from .models import Orders

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = [
            'items_json', 'userId', 'amount', 'name', 
            'email', 'address', 'city', 'state', 
            'zip_code', 'phone', 'payment_method', 
            'payment_comments'
        ]


from django import forms
from .models import GroceryItem

class GroceryItemForm(forms.ModelForm):
    class Meta:
        model = GroceryItem
        fields = ['name', 'quantity', 'price', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }