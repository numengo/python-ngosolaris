#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ngosolaris` package."""
from click.testing import CliRunner

from ngosolaris.cli import cli

# PROTECTED REGION ID(ngosolaris.tests.test_ngosolaris) ENABLED START

def test_ngosolaris():
    from ngosolaris import Cell, AddressBook
    # assert solaris
    cell = Cell(
        cell_id='Cote Basque Nord 64',
        cell_dir='/Users/cedric/Devel/admin/SOLARIS/annuaire/cote_basque_nord',
    )
    #cell.load_members()
    addr_book = AddressBook(cell)
    addr_book.write_member_updated_forms()
    addr_book.write_edition()


if __name__ == '__main__':
    # to run test file standalone
    test_ngosolaris()

# PROTECTED REGION END
