from haralyzer import HarParser
from urllib import parse
import json


def parsing_zaproxy(zaproxy_file_path, exclude_extensions):
	"""
		Parse the txt from the zaproxy output

		Return a list of path
	"""

	print("[Parsing zaproxy file]")
	paths = []
	try:
		with open(zaproxy_file_path) as f:
			har_parser = HarParser(json.loads(f.read()))
			for x in har_parser.har_data["entries"]:
				req = x["request"]
				url = parse.urlsplit(req["url"])
				dict_params = get_params_from_zaproxy(req)
				paths.append([url, dict_params])
	except:
		print(f"\tError can't parse your file : {zaproxy_file_path}")
		print("\tIt must be in har format, go to [https://github.com/Liodeus/Crawlmap/wiki/Zaproxy], to see some examples.")
		exit()
	
	return paths


def get_params_from_zaproxy(request):
	"""
		TODO
	"""

	dict_params = {
		"[GET]": [],
		"[POST]": [],
		"[UPLOAD]": []
	}
	method = request["method"]
	
	if method == "GET":
		data = [dict_params["[GET]"].append(x["name"]) for x in request["queryString"]]
	elif method == "POST":
		mime_type = request["postData"]["mimeType"]

		if "multipart/form-data" in mime_type:
			data = request["postData"]["text"]
			if data:
				data = [dict_params["[UPLOAD]"].append(x.split('; ')[1].split('="')[1].strip()[:-1]) for x in data.split('\n') if "name=" in x]
		else:
			data = [dict_params["[POST]"].append(x["name"]) for x in request["postData"]["params"]]

	return dict_params
