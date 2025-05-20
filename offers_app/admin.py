from django import forms
from django.contrib import admin
from .models import Offer, OfferDetail
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from django import forms
from .models import OfferDetail


class OfferDetailAdminForm(forms.ModelForm):
    features_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 60}),
        required=False,
        label='Features (ein Eintrag pro Zeile)',
        help_text='Bitte jeden Eintrag in eine neue Zeile schreiben.',
    )

    class Meta:
        model = OfferDetail
        exclude = ['features']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and isinstance(self.instance.features, list):
            self.fields['features_text'].initial = '\n'.join(
                self.instance.features)

    def clean(self):
        cleaned_data = super().clean()
        features_text = cleaned_data.get('features_text', '')
        features_list = [line.strip()
                         for line in features_text.split('\n') if line.strip()]
        cleaned_data['features'] = features_list
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        features_text = self.cleaned_data.get('features_text', '')
        features_list = [line.strip()
                         for line in features_text.split('\n') if line.strip()]
        instance.features = features_list  # ← Hier passiert die Magie
        if commit:
            instance.save()
        return instance


class RequiredOfferDetailFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        valid_forms = [
            form for form in self.forms
            if not form.cleaned_data.get('DELETE', False) and not form.cleaned_data.get('price') is None
        ]

        if not valid_forms:
            raise ValidationError(
                "Mindestens ein Angebots-Detail mit Preis muss ausgefüllt werden.")


class OfferDetailInline(admin.StackedInline):  
    model = OfferDetail
    form = OfferDetailAdminForm  
    formset = RequiredOfferDetailFormSet
    extra = 1
    classes = ['collapse']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    inlines = [OfferDetailInline]
