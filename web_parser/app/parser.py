import logging
import pytz

from pytz.tzinfo import DstTzInfo
from datetime import datetime

import django.conf

from bs4 import BeautifulSoup


from requests import Session, Response

from web_parser.models import RegistrationCredential


logger = logging.getLogger(__name__)


class ParserMeta(type):
    def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        cls.session = Session()
        return cls


class WebParser(metaclass=ParserMeta):
    tz: DstTzInfo = pytz.timezone(django.conf.settings.TIME_ZONE)
    credentials: dict = dict()
    resource: str = 'https://zakupki.gov.ru'
    search_path: str = '/epz/organization/search/results.html'
    headers: dict = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }
    request_payload = {
        'morphology': 'on',
        'fz94': 'on',
        'fz223': 'on',
        'F': 'on',
        'S': 'on',
        'M': 'on',
        'NOT_FSM': 'on',
        'registered94': 'on',
        'notRegistered': 'on',
        'sortBy': 'NAME',
        'pageNumber': 1,
        'sortDirection': 'false',
        'recordsPerPage': '_10',
        'showLotsInfoHidden': 'false',
    }

    @classmethod
    def to_dict(cls, data: list) -> None:
        for item in data:
            if item == '\n':
                data.remove('\n')
            else:
                continue
        k, v = data[0].text.strip(), data[1].text.strip()
        if k == 'Дата регистрации':
            if v == '--.--.----':
                v = None
            else:
                v = v.replace('.', '/')
                v = cls.tz.localize(datetime.strptime(v, '%d/%m/%Y'))
        if k == 'Дата/время последнего изменения записи об организации':
            if k is not None:
                v = v.replace('.', '/')
                v = cls.tz.localize(datetime.strptime(v, '%d/%m/%Y %H:%M:%S'))
        cls.credentials.update({k: v})

    @classmethod
    def create_organization(cls, creds_dict: dict) -> None:
        new_record: RegistrationCredential = RegistrationCredential.objects.create(
            full_name=creds_dict.get('Полное наименование'),
            short_name=creds_dict.get('Сокращенное наименование'),
            registry_code=creds_dict.get('Код по Сводному реестру'),
            registration_date=creds_dict.get('Дата регистрации'),
            changed_at=creds_dict.get('Дата/время последнего изменения записи об организации'),
            identification_number=creds_dict.get('ИНН'),
            registration_reason_code=creds_dict.get('КПП'),
            state_registration_number=creds_dict.get('ОГРН'),
            classifier_of_municipal_territories=creds_dict.get('ОКТМО'),
            location_address=creds_dict.get('Место нахождения')
        )
        new_record.save()
        cls.credentials.clear()

    @classmethod
    def parse_credentials(cls, creds: Response) -> None:
        parser: BeautifulSoup = BeautifulSoup(creds.text, 'html.parser')
        for i in parser.body.find_all(attrs={'class': 'blockInfo__section section'}, limit=10):
            cls.to_dict(i.contents)
        cls.create_organization(cls.credentials)

    @classmethod
    def get_organization_link(cls, response):
        href_tag, onclick_tag = response.a.get('href'), response.a.get('onclick')
        if href_tag:
            return href_tag
        if onclick_tag:
            link_fz_44 = onclick_tag.split(',')[1].translate(
                {ord(c): None for c in "'\\)"}
            )
            link_fz_223 = onclick_tag.split(',')[2].translate(
                {ord(c): None for c in "'\\)"}
            )
            return [link_fz_44.strip(), link_fz_223.strip()]
        else:
            return None

    @classmethod
    def get_credentials(cls, doc: Response) -> None:
        links = []
        parser: BeautifulSoup = BeautifulSoup(doc.text, 'html.parser')
        for i in parser.body.find_all(
                'div',
                attrs={'class': 'registry-entry__header-mid__number'}
        ):
            org_link = cls.get_organization_link(i)
            if isinstance(org_link, list):
                links.extend(org_link)
            else:
                links.append(org_link)
        for link in links:
            creds: Response = cls.session.get(
                f"{cls.resource}{link}",
                timeout=5,
                data=cls.request_payload,
                headers=cls.headers
            )
            cls.parse_credentials(creds)

    @classmethod
    def get_search_results(cls) -> None:
        resource, headers = cls.resource, cls.headers
        url, payload = f"{resource}{cls.search_path}", cls.request_payload
        doc: Response = cls.session.get(url, timeout=5, data=payload, headers=headers)
        cls.get_credentials(doc)
