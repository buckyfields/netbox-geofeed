from django import forms

from ipam.models import IPRange, Prefix
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, TagFilterField

from .models import Geofeed

__all__ = (
    'GeofeedFilterForm',
    'GeofeedForm',
)


class GeofeedForm(NetBoxModelForm):
    prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label='Prefix',
        help_text='Assign this geofeed entry to a prefix.',
    )
    ip_range = DynamicModelChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label='IP range',
        help_text='Or, assign this geofeed entry to an IP range instead.',
    )
    comments = CommentField()

    fieldsets = (
        ('Assignment', ('prefix', 'ip_range')),
        ('Geolocation', ('country', 'region', 'city', 'postal_code')),
        ('Notes', ('comments', 'tags')),
    )

    class Meta:
        model = Geofeed
        fields = (
            'prefix', 'ip_range', 'country', 'region', 'city', 'postal_code', 'comments', 'tags',
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()

        if instance is not None and instance.pk and instance.assigned_object is not None:
            if isinstance(instance.assigned_object, Prefix):
                initial.setdefault('prefix', instance.assigned_object)
            elif isinstance(instance.assigned_object, IPRange):
                initial.setdefault('ip_range', instance.assigned_object)

        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        prefix = cleaned_data.get('prefix')
        ip_range = cleaned_data.get('ip_range')

        if prefix and ip_range:
            raise forms.ValidationError('Select either a prefix or an IP range, not both.')
        if not prefix and not ip_range:
            raise forms.ValidationError('Select a prefix or an IP range to assign this geofeed entry to.')

        self.instance.assigned_object = prefix or ip_range

        return cleaned_data


class GeofeedFilterForm(NetBoxModelFilterSetForm):
    model = Geofeed

    country = forms.CharField(required=False)
    region = forms.CharField(required=False)
    city = forms.CharField(required=False)
    postal_code = forms.CharField(required=False)
    tag = TagFilterField(Geofeed)
