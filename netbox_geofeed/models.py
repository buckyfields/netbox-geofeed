from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from ipam.models import IPRange, Prefix
from netbox.models import NetBoxModel

__all__ = (
    'Geofeed',
)

alpha2_validator = RegexValidator(
    regex=r'^[A-Za-z]{2}$',
    message='Enter a valid ISO 3166-1 alpha-2 country code (e.g. US, DE, JP).',
)

region_validator = RegexValidator(
    regex=r'^[A-Za-z]{2}-[A-Za-z0-9]{1,3}$',
    message='Enter a valid ISO 3166-2 region code (e.g. US-CA, GB-LND).',
)


class Geofeed(NetBoxModel):
    """
    An RFC 8805 geolocation record, assigned to either a Prefix or an
    IPRange. A single feed of all Geofeed records can be exported as CSV
    per the RFC 8805 self-published geofeed format.
    """
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(app_label='ipam', model__in=['prefix', 'iprange']),
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id',
    )

    country = models.CharField(
        max_length=2,
        validators=[alpha2_validator],
        help_text='ISO 3166-1 alpha-2 country code',
    )
    region = models.CharField(
        max_length=10,
        blank=True,
        validators=[region_validator],
        help_text='ISO 3166-2 region code (e.g. US-CA)',
    )
    city = models.CharField(
        max_length=100,
        blank=True,
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )
    comments = models.TextField(blank=True)

    clone_fields = ('country', 'region', 'city', 'postal_code')

    class Meta:
        ordering = ('assigned_object_type', 'assigned_object_id')
        verbose_name = 'geofeed'
        verbose_name_plural = 'geofeeds'
        constraints = (
            models.UniqueConstraint(
                fields=('assigned_object_type', 'assigned_object_id'),
                name='netbox_geofeed_geofeed_unique_assignment',
            ),
        )

    def __str__(self):
        if self.assigned_object:
            return f'Geofeed for {self.assigned_object}'
        return f'Geofeed {self.pk}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_geofeed:geofeed', args=[self.pk])

    def clean(self):
        super().clean()
        if self.country:
            self.country = self.country.upper()
        if self.region:
            self.region = self.region.upper()

    def get_cidrs(self):
        """
        Return a list of CIDR strings (as required by RFC 8805's
        "IP Prefix" column) covering this entry's assigned object. A Prefix
        maps to a single CIDR; an IPRange is decomposed into the minimal
        set of CIDR blocks that cover it.
        """
        obj = self.assigned_object

        if isinstance(obj, Prefix):
            return [str(obj.prefix)]

        if isinstance(obj, IPRange):
            return [str(cidr) for cidr in obj.range.cidrs()]

        return []
