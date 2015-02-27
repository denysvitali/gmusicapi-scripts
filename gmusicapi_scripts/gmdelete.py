#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to delete songs from your Google Music library using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdelete.py (-h | --help)
  gmdelete.py [options] [-f FILTER]...

Options:
  -h, --help                         Display help message.
  -u USERNAME, --user USERNAME       Your Google username or e-mail address.
  -p PASSWORD, --pass PASSWORD       Your Google or app-specific password.
  -l, --log                          Enable gmusicapi logging.
  -d, --dry-run                      Output list of songs that would be deleted.
  -q, --quiet                        Don't output status messages.
                                     With -l,--log will display gmusicapi warnings.
                                     With -d,--dry-run will display song list.
  -f FILTER, --filter FILTER         Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                     Songs can match any filter criteria.
                                     This option can be set multiple times.
  -a, --all                          Songs must match all filter criteria.
  -y, --yes                          Delete songs without asking for confirmation.
"""

from __future__ import unicode_literals

import logging

from docopt import docopt

from gmusicapi_wrapper import MobileClientWrapper

QUIET = 25
logging.addLevelName(25, "QUIET")

logger = logging.getLogger('gmusicapi_wrapper')
sh = logging.StreamHandler()
logger.addHandler(sh)


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	mcw = MobileClientWrapper()
	mcw.login(cli['user'], cli['pass'])

	filters = [tuple(filt.split(':', 1)) for filt in cli['filter']]

	delete_songs, _ = mcw.get_google_songs(filters=filters, filter_all=cli['all'])

	if cli['dry-run']:
		logger.info("Found {0} songs to delete".format(len(delete_songs)))

		if delete_songs:
			logger.info("\nSongs to delete:\n")

			for song in delete_songs:
				title = song.get('title', "<empty>")
				artist = song.get('artist', "<empty>")
				album = song.get('album', "<empty>")
				song_id = song['id']

				logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
		else:
			logger.info("\nNo songs to delete")
	else:
		if delete_songs:
			confirm = cli['yes'] or cli['quiet']

			if confirm or raw_input("Are you sure you want to delete {0} song(s) from Google Music? (y/n) ".format(len(delete_songs))) in ("y", "Y"):
				logger.info("\nDeleting {0} songs from Google Music\n".format(len(delete_songs)))

				songnum = 0
				total = len(delete_songs)
				pad = len(str(total))

				for song in delete_songs:
					mcw.api.delete_songs(song['id'])
					songnum += 1

					title = song.get('title', "<empty>")
					artist = song.get('artist', "<empty>")
					album = song.get('album', "<empty>")
					song_id = song['id']

					logger.debug("Deleting {0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
					logger.info("Deleted {num:>{pad}}/{total} song(s) from Google Music".format(num=songnum, pad=pad, total=total))
			else:
				logger.info("No songs deleted.")
		else:
			logger.info("No songs to delete")

	mcw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()