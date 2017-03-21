from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import requests
import json
from math import hypot



def get_ubike_data():
    response = requests.request("GET", "http://data.taipei/youbike")
    return response.json()

def check_is_in_Taipei_city(lat, lng):
    google_api = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(lat)+","+str(lng)+"&key=AIzaSyAjuKYDNlBfEfVZd5JUBMFxFrDkRuH1HyI"
    response = requests.request("GET", google_api)
    address = response.json()["results"][0]["formatted_address"]
    if(address.find("Taipei City")!=-1 and address.find("New Taipei City")==-1):
        return 1#in taipei city
    else:
        return 0#not in taipei city

def get_nearst2_stations(station_data, query_lat, query_lng):
    min_distance1 = 1
    min_distance2 = 1
    nearst_station_num_1 = 0
    nearst_station_num_2 = 0
    for station_idx in station_data:
        each_station_data = station_data[station_idx]
        if each_station_data["act"] is '1' and each_station_data["sbi"] is not '0':
            distance = hypot(query_lat-float(each_station_data["lat"]), query_lng-float(each_station_data["lng"]))
            each_station_data["distance"] = distance
            if distance < min_distance2:
                if distance < min_distance1:
                    min_distance2 = min_distance1
                    nearst_station_num_2 = nearst_station_num_1
                    min_distance1 = distance
                    nearst_station_num_1 = each_station_data["sno"]
                else:
                    min_distance2 = distance
                    nearst_station_num_2 = each_station_data["sno"]

    return nearst_station_num_1, nearst_station_num_2

def ubike(request):
    status_code = "-3"
    result = []
    if request.GET['lat'] and request.GET['lng']:#lat or lng is set or not
        lat = request.GET['lat']
        lng = request.GET['lng']
        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            status_code = "-1"

        if isinstance(lat, float) and isinstance(lng, float):

            # in_taipei_city = check_is_in_Taipei_city(lat, lng)

            if(check_is_in_Taipei_city(lat, lng)):#in taipei city
                station_list = get_ubike_data()
                if station_list["retCode"] != 1:#request ubike data again
                    station_list = get_ubike_data()
                    station_data = station_list["retVal"];
                else:
                    station_data = station_list["retVal"];

                nearst_station_1, nearst_station_2 = get_nearst2_stations(station_data, lat, lng)

                if station_data[nearst_station_1]["bemp"] is '0' and station_data[nearst_station_2]["bemp"] is '0' :
                    status_code = "1"
                else:
                    status_code = "0"

                result = [
                {'station':station_data[nearst_station_1]["sna"],
                'num_ubike':station_data[nearst_station_1]["sbi"]},
                {'station':station_data[nearst_station_2]["sna"],
                'num_ubike':station_data[nearst_station_2]["sbi"]}
                ]
            else:
                status_code = "-2"
    else:
        status_code = "-1"

    data = {
    'code': status_code,
    'result': result
    }
    return JsonResponse(data)
