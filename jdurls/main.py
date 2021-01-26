#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from pathlib import Path
import json
import click
import zipfile

DEFAULT_ZIPFILE_PREFIX = 'linkcollector'
DEFAULT_CONFIG_DIR = 'cfg'
DEFAULT_PATH = Path('~/jd2').expanduser()


@click.command()
@click.option('--contains', default='', help='Display only the urls that contains this text')
@click.option('--urls', is_flag=True, show_default=True, help='Display only urls, no descriptions')
@click.option('--path', default=str(DEFAULT_PATH), show_default=True, type=click.Path(exists=True), help='Pathname of JDownloader2')
def main(path, contains, urls):
    """Display source urls from JDownloader2 LinkGrabber.
    """
    # There is no support for Pathlib.Path as default value
    cfg_dir = Path(path).joinpath(DEFAULT_CONFIG_DIR)

    # Check if exist config subdir
    if cfg_dir.exists():
        desc_set = set()
        # Get all the zip files with the prefix
        for zip_pathname in cfg_dir.glob(f"{DEFAULT_ZIPFILE_PREFIX}*.zip"):
            # Check if is a real zip file
            if zipfile.is_zipfile(zip_pathname):
                with zipfile.ZipFile(zip_pathname) as zipObj:
                    # Get all the filenames inside zip file
                    for zipEntryName in zipObj.namelist():
                        with zipObj.open(zipEntryName) as jsonfile:
                            try:
                                jsdata = json.load(jsonfile)
                                if "downloadLink" in jsdata:
                                    description = click.style(jsdata['downloadLink']['name'])
                                    # No duplicates
                                    if description not in desc_set:
                                        desc_set.add(description)
                                        if not urls:
                                            click.secho(description, fg='blue')
                                        for url in jsdata["sourceUrls"]:
                                            if contains in url:
                                                click.echo(url)
                            except Exception:
                                click.secho(f"Error while decoding JSON file {zipEntryName} inside {zip_pathname}", fg='yellow')
                                raise click.Abort()
        if len(desc_set) == 0:
            click.secho("No source urls found!", fg='yellow')
    else:
        click.secho(f"JDownloader2 config directory not found in: {path}", fg='yellow')
        raise click.Abort()


if __name__ == "__main__":
    main()
