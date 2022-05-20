

def parsing_zaproxy(zaproxy_file_path, exclude_extensions):
	"""
		Parse the txt from the zaproxy output

		Return a list of path
	"""

	print("[Parsing zaproxy file]")
	paths = []

	try:
		with open(zaproxy_file_path) as f:
			for line in f:
				url = parse.urlsplit(line)
				paths.append(url)
	except FileNotFoundError:
		print(f"Error can't parse your file : {zaproxy_file_path}")
		print("It must be in txt format, go to [https://github.com/Liodeus/Crawlmap/wiki/Zaproxy], to see some examples.")
		exit()
	
	return paths