# import argparse
# import requests


# def parse_xpn(text):
#     return [
#         {'song_name': '', 'artist_name': '', 'album_name': ''},
#     ]


# def main(args=None):
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '--refresh-token',
#         required=True,
#         help='Get this token from spotify'
#     )
#     parser.add_argument(
#         '--client-id',
#         required=True,
#         help='spotify api client id'
#     )
#     parser.add_argument(
#         '--client-secret',
#         required=True,
#         help='spotify api client secret',
#     )

#     cli_args = parser.parse_args(args=args)
#     refresh_token = cli_args.refresh_token
#     client_id = cli_args.client_id
#     client_secret = cli_args.client_secret

#     url = 'xpn.org/playlist'

#     r = requests.get(url)
#     text = r.text
#     parsed_page = parse_xpn(text)








# # scrape the song information from the website
# # match things up to stuff on spotify
# # create a playlist of spotify songs

