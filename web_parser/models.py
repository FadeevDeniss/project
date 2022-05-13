import logging

from django.db.models import Model, TextField, CharField, DateField, DateTimeField

logger = logging.getLogger(__name__)


class RegistrationCredential(Model):
    full_name = TextField(blank=True, editable=True, verbose_name='Полное наименование', null=True)
    short_name = CharField(blank=True, editable=True, max_length=100, verbose_name='Краткое наименование', null=True)

    registry_code = CharField(
        blank=True,
        editable=True,
        max_length=100,
        verbose_name='Код по Сводному реестру',
        null=True
    )

    registration_date = DateField(blank=True, null=True)
    changed_at = DateTimeField(blank=True, null=True)

    identification_number = TextField(blank=True, editable=True, verbose_name='ИНН', null=True)
    registration_reason_code = TextField(blank=True, editable=True, verbose_name='КПП', null=True)
    state_registration_number = TextField(blank=True, verbose_name='ОГРН', null=True)
    classifier_of_municipal_territories = TextField(blank=True, verbose_name='ОКТМО', null=True)

    location_address = TextField(blank=True, editable=True, verbose_name='Место нахождения', null=True)

    def __repr__(self):
        return f"Наименование: {self.short_name}, ИНН: {self.identification_number}, " \
               f"КПП: {self.registration_reason_code}"








