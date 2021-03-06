# -*- coding: utf-8 -*-

"""Main module Address Book """
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
from .cell import Cell

FORM_PAGE = Path(settings.FORM_PAGE)
COVER_PAGE = Path(settings.COVER_PAGE)
ADDR_BOOK_PAGE = Path(settings.ADDR_BOOK_PAGE)

FORM_PAGE = str(FORM_PAGE.resolve()) if FORM_PAGE.exists()\
    else str(Path(__file__).parent.joinpath(settings.FORM_PAGE).resolve())
COVER_PAGE = str(COVER_PAGE.resolve()) if COVER_PAGE.exists()\
    else str(Path(__file__).parent.joinpath(settings.COVER_PAGE).resolve())
ADDR_BOOK_PAGE = str(ADDR_BOOK_PAGE.resolve()) if ADDR_BOOK_PAGE.exists()\
    else str(Path(__file__).parent.joinpath(settings.ADDR_BOOK_PAGE).resolve())


class AddressBook(with_metaclass(SchemaMetaclass)):
    _id = r"https://solaris-france.org#/$defs/AddressBook"

    def __init__(self, cell):
        ObjectProtocol.__init__(self)
        self.cell = cell

        self.edition = f'{date.today().isoformat()}'
        self.edition_fmt = f'{date.today().strftime("%d/%m/%Y")}'
        self.edition_fp = cell.cell_dir.joinpath(f'annuaire-solaris-{cell.cell_id}-{self.edition}.pdf')

        build_dir = self.cell.build_dir
        self.build_ed_dir = build_ed_dir = build_dir.joinpath(self.edition)
        self.forms_updated_dir = forms_updated_dir = build_ed_dir.joinpath('forms')
        self.index_fp = build_ed_dir.joinpath('index.pdf')

        if not build_dir.exists():
            os.makedirs(str(build_dir))
            self._logger.info('CREATE DIRECTORY %s.' % build_dir)
        if not build_ed_dir.exists():
            os.makedirs(str(build_ed_dir))
            self._logger.info('CREATE DIRECTORY %s.' % build_ed_dir)
        if not forms_updated_dir.exists():
            os.makedirs(str(forms_updated_dir))
            self._logger.info('CREATE DIRECTORY %s.' % build_ed_dir)

    def _write_member_pages(self):
        cell_id = self.cell.cell_id
        for member in self.cell.members:
            member_page = pdfrw.PdfReader(ADDR_BOOK_PAGE)
            mfp = self.build_ed_dir.joinpath(member['PageFilename']+'.pdf')
            member['PageFilepath'] = mfp
            member['EditionFilenameField'] = self.edition_fp.stem
            member_writer = pdfrw.PdfWriter(str(mfp))
            annotations = member_page.pages[0][ANNOT_KEY]
            for annotation in annotations:
                if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                    if annotation[ANNOT_FIELD_KEY]:
                        key = annotation[ANNOT_FIELD_KEY][1:-1]
                        new_key = key + member['PageField']
                        if key in member.keys():
                            if type(member[key]) == bool:
                                if member[key] == True:
                                    annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes'), T=new_key))
                            else:
                                val = member[key]
                                val = pdfrw.PdfString.from_unicode(val)
                                if val:
                                    if key in ['EmailField', 'TelegramIdField']:
                                        link_key = key.replace('Field', 'Link')
                                        #annotation.AA.D.URI = pdfrw.PdfString.from_unicode(link)
                                        #annotation.AA.D.update(pdfrw.PdfDict(V=val))
                                annotation.update(pdfrw.PdfDict(V=val, T=new_key, AP=''))
                    annotation.update(pdfrw.PdfDict(Ff=1))
            member_page.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            member_writer.addpages(member_page.pages)
            member_writer.trailer.Info = pdfrw.IndirectPdfDict(
                Title=member['TitleField'],
                Author=f'SOLARIS {cell_id}',
                Creator=f'SOLARIS {cell_id}',
                Subject=f'Annuaire SOLARIS {cell_id} {self.edition_fmt}'
            )
            member_writer.trailer.Root.AcroForm = member_page.Root.AcroForm
            member_writer.trailer.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            member_writer.write()
            self._logger.info('CREATE FILE %s.' % mfp)
        return self

    def _write_index(self):
        doc = SimpleDocTemplate(str(self.index_fp),
                                pagesize=A4)

        w, h = doc.width, doc.height

        flowables = []

        header1_style = ParagraphStyle(name='IndexHeading', fontSize=18)
        header2_style = ParagraphStyle(name='IndexHeading2', fontSize=14)
        toc_entry_style = ParagraphStyle(name='toc', fontSize=12, leading=14, alignment=TA_JUSTIFY)
        fn = toc_entry_style.fontName
        fs = toc_entry_style.fontSize
        w = doc.width - 20
        dot = '.'
        dotw = stringWidth(dot, fn, fs)

        flowables.append(Paragraph('<b>Index</b>', style=header1_style))
        flowables.append(Spacer(width=0, height=settings.INDEX_TITLE_SPACE))
        for member in self.cell.members:
            ptext = member['IndexEntryField']
            pagestr = member['PageField']
            page = int(pagestr)
            availWidth = w - stringWidth(ptext+pagestr, fn, fs)
            dotsn = int(availWidth / dotw)
            toc_entry = '%s%s%s' % (ptext, dotsn * dot, pagestr)
            flowables.append(Paragraph(toc_entry, style=toc_entry_style))
        flowables.append(PageBreak())

        flowables.append(Paragraph('<b>Index par ville</b>', header1_style))
        flowables.append(Spacer(width=0, height=settings.INDEX_TITLE_SPACE))
        for city, members in self.cell.members_city.items():
            flowables.append(Spacer(width=0, height=settings.TOC_SPACE))
            flowables.append(Paragraph(f'<b>{city}</b>', style=header2_style))
            flowables.append(Spacer(width=0, height=settings.TOC_SPACE))
            for member in members:
                ptext = member['IndexCityEntryField']
                pagestr = member['PageField']
                page = int(pagestr)
                availWidth = w - stringWidth(ptext+pagestr, fn, fs)
                dotsn = int(availWidth / dotw)
                toc_entry = '%s%s%s' % (ptext, dotsn * dot, pagestr)
                flowables.append(Paragraph(toc_entry, style=toc_entry_style))

        doc.build(flowables)
        self._logger.info('CREATE FILE %s.' % self.index_fp)

    def _compile_write(self):
        cell_id = self.cell.cell_id
        all_writer = pdfrw.PdfWriter(str(self.edition_fp))
        bookmarks = []
        bookmarksDict = {}

        def addBookmark(title, pageNum, parent=None):
            '''
            Adds a new bookmark entry.
            pageNum must be a valid page number in the writer
            and parent can be a bookmark object returned by a previous addBookmark call
            '''
            try:
                page = all_writer.pagearray[pageNum]
            except IndexError:
                # TODO: Improve error handling ?
                pdfrw.errors.PdfOutputError("Invalid page number: " % (pageNum))

            bookmark = {
                'title': title,
                'page': page,
                'childs': []
            }
            bid = id(bookmark)

            if not parent:
                bookmarks.append(bookmark)

            else:
                parentObj = bookmarksDict.get(id(parent), None)
                if not parentObj:
                    pdfrw.errors.PdfOutputError("Bookmark parent object not found: " % parent)

                parentObj['childs'].append(bookmark)

            bookmarksDict[bid] = bookmark
            return bookmark

        # cover
        cover_reader = pdfrw.PdfReader(COVER_PAGE)
        cover_annotations = cover_reader.pages[0][ANNOT_KEY]
        for annotation in cover_annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    if key == 'CellField':
                        annotation.update(pdfrw.PdfDict(V=pdfrw.PdfString.from_unicode(cell_id), AP=''))
                    if key == 'EditionField':
                        annotation.update(pdfrw.PdfDict(V=pdfrw.PdfString.from_unicode(self.edition_fmt), AP=''))
        all_writer.addpages(cover_reader.pages)

        all_writer.addpage(create_blank_page())
        n0 = len(all_writer.pagearray)

        for member in self.cell.members:
            member_reader = pdfrw.PdfReader(ADDR_BOOK_PAGE)
            all_writer.addpages(member_reader.pages)
            annotations = all_writer.pagearray[-1][ANNOT_KEY]
            for annotation in annotations:
                if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                    if not annotation[ANNOT_FIELD_KEY]:
                        annotation = annotation[ANNOT_PARENT_KEY]
                    if annotation[ANNOT_FIELD_KEY]:
                        key = annotation[ANNOT_FIELD_KEY][1:-1]
                        # create an aliased field based on page number / avoid conflict between multiple forms data
                        new_key = key + member['PageField']
                        if key in member.keys():
                            val = member[key]
                            if type(member[key]) == bool:
                                if member[key] == True:
                                    annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes')))
                            elif val:
                                val = pdfrw.PdfString.from_unicode(member[key])
                                if key in ['EmailLinkField', 'TelegramIdLinkField']:
                                    pass
                                annotation.update(pdfrw.PdfDict(V=val, T=new_key, AP=''))
                    annotation.update(pdfrw.PdfDict(Ff=1))
            real_page_num = n0+int(member['PageField'])-1
            addBookmark(member['TitleField'], real_page_num)

        all_writer.addpage(create_blank_page())
        # index
        index_reader = pdfrw.PdfReader(str(self.index_fp))
        all_writer.addpages(index_reader.pages)

        # Recursive function to build outlines tree
        # https://github.com/pmaupin/pdfrw/issues/52
        def buildOutlines(parent, bookmarks):

            outline = None

            if bookmarks:
                outline = pdfrw.IndirectPdfDict()
                outline.Count = len(bookmarks)

                first = None
                next = None
                last = None

                for b in bookmarks:

                    newb = pdfrw.IndirectPdfDict(
                        Parent=parent or outline,
                        Title=b['title'],
                        A=pdfrw.IndirectPdfDict(
                            D=pdfrw.PdfArray((b['page'], pdfrw.PdfName('Fit'))),
                            S=pdfrw.PdfName('GoTo')
                        )
                    )

                    if not first:
                        first = newb

                    else:
                        last.Next = newb
                        newb.Prev = last

                    last = newb

                    # Add children, if any.
                    if b['childs']:
                        childOutline = buildOutlines(newb, b['childs'])
                        newb.First = childOutline.First
                        newb.Last = childOutline.Last
                        newb.Count = childOutline.Count

                outline.First = first
                outline.Last = last

            return outline

        # Testing for now, only add root level bookmarks
        outlines = buildOutlines(None, bookmarks)

        if outlines:
            all_writer.trailer.Root.Outlines = outlines
        all_writer.trailer.Info = pdfrw.IndirectPdfDict(
            Title=f'Annuaire SOLARIS {cell_id} {self.edition_fmt}',
            Author=f'SOLARIS {cell_id}',
            Creator=f'SOLARIS {cell_id}'
        )
        all_writer.trailer.Root.AcroForm = cover_reader.Root.AcroForm
        all_writer.trailer.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
        all_writer.write()
        self._logger.info('CREATE FILE %s.' % self.edition_fp)
        return self

    def write_edition(self):
        self._write_member_pages()
        self._write_index()
        self._compile_write()
        return self

    def write_member_updated_forms(self):
        cell_id = self.cell.cell_id
        forms = []
        for member in self.cell.members:
            member_page = pdfrw.PdfReader(FORM_PAGE)
            mfp = self.forms_updated_dir.joinpath(member['PageFilename']+'.pdf')
            forms.append(mfp)
            member['FormUpdatedFilepath'] = mfp
            member['EditionFilenameField'] = self.edition_fp.stem
            member_writer = pdfrw.PdfWriter(str(mfp))
            annotations = member_page.pages[0][ANNOT_KEY]
            for annotation in annotations:
                if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                    if annotation[ANNOT_FIELD_KEY]:
                        key = annotation[ANNOT_FIELD_KEY][1:-1]
                        new_key = key + member['PageField']
                        if key in member.keys():
                            if type(member[key]) == bool:
                                if member[key] == True:
                                    annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes'), T=new_key))
                            else:
                                val = member[key]
                                val = pdfrw.PdfString.from_unicode(val)
                                if val:
                                    if key in ['EmailField', 'TelegramIdField']:
                                        link_key = key.replace('Field', 'Link')
                                        #annotation.AA.D.URI = pdfrw.PdfString.from_unicode(link)
                                        #annotation.AA.D.update(pdfrw.PdfDict(V=val))
                                annotation.update(pdfrw.PdfDict(V=val, T=new_key, AP=''))
            member_page.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            member_writer.addpages(member_page.pages)
            member_writer.trailer.Info = pdfrw.IndirectPdfDict(
                Title=member['TitleField'],
                Author=f'SOLARIS {cell_id}',
                Creator=f'SOLARIS {cell_id}',
                Subject=f'Formulaire SOLARIS {cell_id} - {self.edition_fmt}'
            )
            member_writer.trailer.Root.AcroForm = member_page.Root.AcroForm
            member_writer.trailer.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            member_writer.write()
            self._logger.info('CREATE FILE %s.' % mfp)
        return forms

