#!/usr/bin/env python

import cnav 

data = {
	"ctRoot": [
		{
			"_id": "6QE2J8TURVDBNQPM",
			"name": "Antionette Darby",
			"dob": "2021-10-27",
			"address": {
				"street": "1680 Lynthorpe Road",
				"town": "Clay Cross",
				"postode": "GU85 4TT"
			},
			"telephone": "+43-6452-894-201",
			"pets": [
				"SUGAR",
				"Milo"
			],
			"score": 7.2,
			"email": "judson_araujo322@voting.com",
			"url": "http://remedy.com",
			"description": "invalid governing treaty bunny diy waste yea self outer lord nat vs judge steve basement values tsunami subsequent at boys",
			"verified": True,
			"salary": 52974
		},
		{
			"_id": "SRDQ59HVJSRFA4OM",
			"name": "Elfriede Kaminski",
			"dob": "2014-10-10",
			"address": {
				"street": "0365 Syndall Lane",
				"town": "Enniskillen",
				"postode": "B4 4DJ"
			},
			"telephone": "+60-2633-655-545",
			"pets": [
				"Lilly",
				"Cooper"
			],
			"score": 2.7,
			"email": "jacques-turk@tested.com",
			"url": "https://www.fighter.com",
			"description": "fool tabs grave suit less voyeurweb leadership candidates amend scientist expected retrieval nextel fundraising government known difference washing republic aggressive",
			"verified": False,
			"salary": 63932
		},
		{
			"_id": "LJTVTJN9J1DDOIF6",
			"name": "Sina Switzer",
			"dob": "2020-11-26",
			"address": {
				"street": "7349 Insall Lane",
				"town": "Leominster",
				"postode": "CH7 3ZJ"
			},
			"telephone": "+31-6615-140-529",
			"pets": [
				"Muffin",
				"Milo"
			],
			"score": 8.4,
			"email": "doreen.self@danny.t3l3p0rt.net",
			"url": "https://illness.com",
			"description": "compile sacramento novelty sometimes thesis various nascar fu theoretical chad certificate patrick finds managers diy abraham wrong adipex march organisations",
			"verified": True,
			"salary": 18973
		},
		{
			"_id": "YN9EI2CG2HRLSFMO",
			"name": "Kermit James",
			"dob": "2018-05-14",
			"address": {
				"street": "3807 Saddlewood",
				"town": "Shotton",
				"postode": "MK35 6RH"
			},
			"telephone": "+350-8232-629-052",
			"pets": [
				"Leo",
				"Riley"
			],
			"score": 8.4,
			"email": "corrie.plunkett73125@realtor.com",
			"url": "http://kai.com",
			"description": "buddy pen retained beaver accepting space employed equality stores unable wealth lemon informed set lambda np fourth cameroon codes mysimon",
			"verified": True,
			"salary": 28561
		},
		{
			"_id": "V63C8TLJVIQNNX0Z",
			"name": "Elene Ness",
			"dob": "2019-10-18",
			"address": {
				"street": "7973 Russell Circle",
				"town": "Barton upon Humber",
				"postode": "EH19 3EO"
			},
			"telephone": "+675-3607-242-384",
			"pets": [
				"Maggie",
				"Penny"
			],
			"score": 4.8,
			"email": "claudia9@fortune.kasuga.fukuoka.jp",
			"url": "https://www.cases.com",
			"description": "wheel poem mime interested amd urw sporting suffering ghost brandon arbitration marker february cameras names pens sprint chad conceptual road",
			"verified": False,
			"salary": 13704
		},
		{
			"_id": "OU4YCQN9BCEL9EH3",
			"name": "Lucrecia Kelly",
			"dob": "2018-01-26",
			"address": {
				"street": "2490 Pennys",
				"town": "Houghton Regis",
				"postode": "SG9 2HD"
			},
			"telephone": "+64-2014-278-118",
			"pets": [
				"Gracie",
				"Mia"
			],
			"score": 1.3,
			"email": "destiny_hennessey39737@yahoo.com",
			"url": "http://validity.com",
			"description": "reader selecting identical deficit judgment reflect venue food incorporate tumor biographies axis coating congress qualifying guestbook called brothers projected knives",
			"verified": True,
			"salary": 20324
		},
		{
			"_id": "AO4JJUZNQI95GU6L",
			"name": "Patty Killian",
			"dob": "2021-01-03",
			"address": {
				"street": "7473 Drywood Lane",
				"town": "Warwick",
				"postode": "GU8 5XS"
			},
			"telephone": "+81-2833-051-191",
			"pets": [
				"Jasper",
				"Cooper"
			],
			"score": 8.2,
			"email": "marta-gamble@hotmail.com",
			"url": "https://www.converter.com",
			"description": "sd error guest reduces hartford flexibility calculated started salem portal participant ap hose anonymous reggae logging tr tea entertainment eminem",
			"verified": False,
			"salary": 62196
		}
	]
}

def check_results(results):
  print("printing results")
  for r in results:
    print(f"type: {type(r)}\n - {r}")
  print(f"type of return: {type(results)}")

nav = cnav.Nav()
res = nav.navigate(data)
check_results(res)
