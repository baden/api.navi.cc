---
title: User account
---
#<%= @item[:title] %>

Standart user accaunt in system.

#Contents
* TOC
{:toc}

## Object "point" # {#obj_point}

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

## Object "event" # {#obj_event}

|-------------------+-----------+----------------------------------------------------------------|
| Field name        | Type      |  Description                                                   |
|-------------------|-----------|----------------------------------------------------------------|
| time              | timestamp | Time when event occured                                        |
| type              | enum()    | Type of the event                                              |
| information       | object    | Additional information for the event, depending on the `type`. |
| ?lat              | float     |                                                                |
| ?lon              | float     |                                                                |
| Additional fields:
| is_approx_time    | boolean   | True when `time` is a server time*                             |
|-------------------+-----------+----------------------------------------------------------------|

## Object "aggregated points" # {#obj_ag_points}

Each object contains aggregated information for the specefied hour.

|------------+--------------+--------------------------------------------------|
| Field name | Type         |  Description                                     |
|------------|--------------|--------------------------------------------------|
| imei       | string       | device imei                                      |
| hour       | int          | Hour for which aggregation was applied           |
| data       | array[points]| Array of the [point](#obj_point)                 |
| events     | array[event] | Array of the [event](#obj_event)                 |
| ?avg_speed | float        | Avarage speed during hour                        |
| ?distance  | float        | Distance                                         |
| ?...       | float        | *unknown*                                        |
|------------+--------------+--------------------------------------------------|





## Retrieving `track` information {#read}

    GET /systems/:imei/tracks


Whithout parametrs the data for the last 24 hours is returned in flat format

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
        ],
        "events" : [
            {
                "time": 1357020002,
                "type": "device_off",
                "information": {},
                "lat": 50.518,
                "lon": 42.4783
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
            ],
            "events" : []
        }
]
~~~
{: .language-javascript}
### Request

    GET /systems/1/tracks?since=0&till=7200

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

## Retrieving `event` information {#read_event}

    GET /systems/:imei/events

Whithout parametrs the events returned for the last 24 hours

Parameters:

* **since** (_timestamp_) - starting timestamp for returned points
* **till**  (_timestamp_) - ind time for the points


### Request

    GET /systems/1/events

### Response

<%= headers 200 %>
~~~
[
    {
        "time": 1357020002,
        "type": "device_off",
        "information": {},
        "lat": 50.518,
        "lon": 42.4783
    }
]
~~~
{: .language-javascript}


