# -*- coding: utf-8 -*-

"""Main module Solaris """
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import logging
from datetime import date
from pathlib import Path
from collections import OrderedDict
import pdfrw, pdfrw.errors, pdfrw.objects, pdfrw.objects.pdfname

from ngoschema.protocols import with_metaclass, SchemaMetaclass, ObjectProtocol

from reportlab.platypus import PageTemplate, BaseDocTemplate, SimpleDocTemplate, Frame
from reportlab.platypus import NextPageTemplate, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY

from . import settings
from .pdfrw_utils import get_form_fields, create_blank_page
from .pdfrw_utils import ANNOT_KEY, SUBTYPE_KEY, WIDGET_SUBTYPE_KEY, ANNOT_FIELD_KEY, ANNOT_PARENT_KEY
from .personas import Member, Administrator, Coordinator


class Cell(with_metaclass(SchemaMetaclass)):
    _id = r"https://solaris-france.org#/$defs/Cell"

    def __init__(self, cell_id, cell_dir):
        ObjectProtocol.__init__(self)
        self.cell_id = cell_id
        self.cell_dir = cell_dir if isinstance(cell_dir, Path) else Path(cell_dir)
        self.cell_dir = self.cell_dir.expanduser().resolve()
        self.member_dir = self.cell_dir.joinpath(settings.MEMBER_DIR)
        self.members = []
        self.build_dir = self.cell_dir.joinpath(settings.BUILD_DIR)
        self.load_members()

    def _read_members(self):
        cyear = date.today().year
        for x in os.listdir(str(self.member_dir)):
            if x.endswith(".pdf"):
                self._logger.info('LOAD FILE %s.' % x)
                pdf_fp = self.member_dir.joinpath(x)
                pdfr = pdfrw.PdfReader(str(pdf_fp))
                # establish gender
                member = get_form_fields(pdfr.pages[0])
                gender = 'M' if member['MaleCheck'] else ''
                gender += 'F' if member['FemaleCheck'] else ''
                # read fields, set gender, compute age and set title
                member['GenderField'] = gender
                firstn = member['FirstNameField']
                lastn = member.get('NameField') or member.get('LastNameField')
                member['LastNameField'] = lastn
                lastn_upper = lastn.upper()
                city = member['CityField']
                city_upper = member['CityUpper'] = city.upper()
                byear = int(member['BirthYearField'].replace('.', '/').split('/')[-1])
                if byear < 100:
                    byear += 1900
                member['BirthYearField'] = str(byear)
                age = cyear - byear
                member['TitleField'] = f'{firstn} {lastn_upper}, {city_upper}, {gender} {age}ans'
                member['IndexEntryField'] = f'{lastn_upper} {firstn}, {city_upper}, {gender} {age}ans'
                member['IndexCityEntryField'] = f'{lastn_upper} {firstn}, {gender} {age}ans'
                member['PageFilename'] = f'{city_upper} - {lastn_upper} {firstn}.pdf'
                member['FormOrigFilepath'] = pdf_fp
                member['EmailLink'] = f'mailto:{member["EmailField"]}'
                member['TelegramIdLink'] = f'https://t.me/{member["TelegramIdField"]}'
                self.members.append(member)

    def _sort_members(self):
        self.members = members = sorted(self.members, key=lambda x: x['IndexEntryField'])
        cities = sorted(list(set([m['CityField'] for m in members])))
        self.members_city = OrderedDict([(c, list()) for c in cities])
        for i, m in enumerate(self.members):
            self.members_city[m['CityField']].append(m)
            m['PageField'] = ip = str(i + 1)

    def load_members(self):
        self._read_members()
        self._sort_members()
        return self
