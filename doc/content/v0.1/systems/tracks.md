---
title: User account
---
#<%= @item[:title] %>

Standart user accaunt in system.

#Contents
* TOC
{:toc}

## Object "point" # {#obj}

|------------+-----------+--------------------------------------------------|
| Field name | Type      |  Description                                     |
|------------|-----------|--------------------------------------------------|
| lon        | float     | Point longtitude                                 |
| lat        | float     | Point latitude                                   |
| vin        | float     | *unknown*                                        |
| vout       | float     | *unknown*                                        |
| fsource    | float     | *unknown*                                        |
| sats       | float     | *unknown*                                        |
| course     | float     | *unknown*                                        |
| speed      | float     | *unknown*                                        |
| time       | timestamp | *unknown*                                        |
|-------------------+---------------+---------------------------------------|

## Object "aggregated points" # {#ag_points}

|------------+-----------+--------------------------------------------------|
| Field name | Type      |  Description                                     |
|------------|-----------|--------------------------------------------------|
| imei       | string    | device imei                                      |
| hout       | int       | Hour for which aggregation was applied           |
| ?avg_speed | float     | Avarage speed during hour                        |
| ?distance  | float     | Distance                                         |
| ?events    | float     | Events during hour                               |
| ?...       | float     | *unknown*                                        |
|-------------------+---------------+---------------------------------------|

## Retrieving track information {#read}

    GET /systems/:imei/tracks


Whithout parametrs data for the last 24 hours is returned

Parameters:

* **since** (_timestamp_) - starting timestamp for returned points
* **till**  (_timestamp_) - ind time for the points
* **format** (_enum(`flat`,`aggregated`)_) - format of the returned values. Default is ?`flat`?

### Request

    GET /systems/1/tracks?since=0&till=7200&format=aggregated

### Response

<%= headers 200 %>
~~~
[
    {
        "imei": "1",
        "hour": 1,
        "data": [
            {
                "fsource": 8,
                "sats": 6,
                "vout": 12,
                "photo": 0,
                "lon": 42.4783,
                "course": 256,
                "vin": 42,
                "time": 1357020000,
                "lat": 50.518,
                "speed": 92.9704
            },
            {
                "fsource": 8,
                "sats": 6,
                "vout": 12,
                "photo": 0,
                "lon": 42.4783,
                "course": 256,
                "vin": 42,
                "time": 1357020001,
                "lat": 50.518,
                "speed": 92.9704
            }
        ]
    },
    {
            "imei": "2",
            "hour": 1,
            "data": [
                {
                    "fsource": 8,
                    "sats": 6,
                    "vout": 12,
                    "photo": 0,
                    "lon": 42.4783,
                    "course": 256,
                    "vin": 42,
                    "time": 1357027200,
                    "lat": 50.518,
                    "speed": 92.9704
                },
                {
                    "fsource": 8,
                    "sats": 6,
                    "vout": 12,
                    "photo": 0,
                    "lon": 42.4783,
                    "course": 256,
                    "vin": 42,
                    "time": 1357027201,
                    "lat": 50.518,
                    "speed": 92.9704
                }
            ]
        }
]
~~~
{: .language-javascript}
### Request

    GET /systems/1/tracks?since=0&till=7200&format=flat

### Response

<%= headers 200 %>
~~~
[
    {
        "fsource": 8,
        "sats": 6,
        "vout": 12,
        "photo": 0,
        "lon": 42.4783,
        "course": 256,
        "vin": 42,
        "time": 1357020000,
        "lat": 50.518,
        "speed": 92.9704
    },
    {
        "fsource": 8,
        "sats": 6,
        "vout": 12,
        "photo": 0,
        "lon": 42.4783,
        "course": 256,
        "vin": 42,
        "time": 1357020001,
        "lat": 50.518,
        "speed": 92.9704
    },
    {
        "fsource": 8,
        "sats": 6,
        "vout": 12,
        "photo": 0,
        "lon": 42.4783,
        "course": 256,
        "vin": 42,
        "time": 1357020000,
        "lat": 50.518,
        "speed": 92.9704
    },
    {
        "fsource": 8,
        "sats": 6,
        "vout": 12,
        "photo": 0,
        "lon": 42.4783,
        "course": 256,
        "vin": 42,
        "time": 1357020001,
        "lat": 50.518,
        "speed": 92.9704
    }
]
~~~
{: .language-javascript}
