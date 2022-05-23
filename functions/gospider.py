from urllib import parse
import json


def parsing_gospider(gospider_file_path, exclude_extensions):
	"""
		Parse the JSON from the Gospider output

		Return a list of path
	"""

	print("[Parsing Gospider file]")
	paths = []
	try:
		with open(gospider_file_path) as f:
			for line in f:
				try:
					data = json.loads(line)
					type_data = data["type"]

					if type_data == "linkfinder":
						url_to_parse = data["source"]
					else:
						url_to_parse = data["output"]
				except json.decoder.JSONDecodeError:
					pass

				url = parse.urlsplit(url_to_parse)
				dict_params = get_params_from_gospider(url)
				paths.append([url, dict_params])
	except:
		print(f"\tError can't parse your file : {gospider_file_path}")
		print("\tIt must be in json format, go to [https://github.com/Liodeus/Crawlmap/wiki/Gospider], to see some examples.")
		exit()
	
	return paths


def get_params_from_gospider(url):
	"""
		Get the parameters from a URL

		Return a dictionnary of GET parameters
	"""

	dict_params = {
		"[GET]": [],
		"[POST]": [],
		"[UPLOAD]": []
	}

	for params in url.query.split('&'):
		if params:
			dict_params["[GET]"].append(params.split('=')[0])

	return dict_params
