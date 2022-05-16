from functions.functions import *
import argparse

## http - https problem

if __name__ == '__main__':
	banner()

	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url", required=True, help="Base URL to filter on", type=str)
	parser.add_argument("-b", "--burp", help="Output from BurSuite (xml)", type=str)
	parser.add_argument("-g", "--gospider", help="Output from Gospider (json)", type=str)
	parser.add_argument("-z", "--zaproxy", help="Output from Zaproxy (txt)", type=str)
	parser.add_argument("-o", "--out", help="Output file", type=str)
	parser.add_argument("--exclude", help="Exclude extensions (Example : \"png,svg,css,ico\")", type=str, default="")
	parser.add_argument("--nofiles", help="Don't print files, only folders", action="store_true", default=False)
	args = parser.parse_args()

	# Getting user input
	burp = args.burp
	gospider = args.gospider
	zaproxy = args.zaproxy
	url = args.url
	domain = parse.urlsplit(url).netloc
	out_file = args.out
	nofiles = args.nofiles
	exclude_extensions = [x.lower() for x in args.exclude.split(',')]

	paths_burp = []
	paths_gospider = []
	paths_zaproxy = []

	if burp:
		paths_burp = parsing_burp(burp, exclude_extensions, url)
		paths_burp = merge_parsing(paths_burp, domain, nofiles, exclude_extensions)

	if gospider:
		paths_gospider = parsing_gospider(gospider, exclude_extensions)
		paths_gospider = merge_parsing(paths_gospider, domain, nofiles, exclude_extensions)

	if zaproxy:
		paths_zaproxy = parsing_zaproxy(zaproxy, exclude_extensions)
		paths_zaproxy = merge_parsing(paths_zaproxy, domain, nofiles, exclude_extensions)

	merge_paths = merge_all_paths(paths_burp, paths_gospider, paths_zaproxy)
	writing_md(merge_paths, url, out_file)
