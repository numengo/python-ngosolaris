import os, sys
import click
from ngoschema.cli import ComplexCLI, base_cli, run_cli
from ngoschema.cli import pass_environment

from ngosolaris import settings
from ngosolaris import Cell, AddressBook

@click.group('annuaire', chain=True)
@pass_environment
@click.option("--cell-id", default=settings.CELL_ID, prompt="Identifiant de cellule", help="Identifiant de la cellule SOLARIS.")
@click.option('--cell-dir', default=settings.CELL_DIR, type=click.Path(), prompt="Répertoire de l annuaire", help="Donner le repertoire de l annuaire contenant le dossier des formulaires.")
def cli(ctx, cell_id, cell_dir):
    __doc__ = Cell.__doc__
    #### PROTECTED REGION ID(solaris.commands.cmd_annuaire.cli) ENABLED START
    cell = Cell(cell_id=cell_id, cell_dir=cell_dir)
    ctx.obj = AddressBook(cell)
    click.echo(str(ctx.obj))
    #### PROTECTED REGION END

@cli.command('compile')
@pass_environment
def compile(ctx):
    __doc__ = AddressBook.write_edition.__doc__
    #### PROTECTED REGION ID(solaris.commands.cmd_annuaire.compile) ENABLED START
    click.echo('CALL write_edition')
    addr_book = ctx.obj
    ret = addr_book.write_edition()
    click.echo('WRITE FILE %s' % addr_book.edition_fp)
    #### PROTECTED REGION END

@cli.command('update')
@pass_environment
def update(ctx):
    __doc__ = AddressBook.write_member_updated_forms.__doc__
    #### PROTECTED REGION ID(solaris.commands.cmd_annuaire.update) ENABLED START
    click.echo('CALL write_member_updated_forms')
    addr_book = ctx.obj
    forms = addr_book.write_member_updated_forms()
    for f in forms:
        click.echo('WRITE FILE %s' % f)
    #### PROTECTED REGION END
