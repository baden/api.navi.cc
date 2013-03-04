---
title: Системы пользователя | api.navi.cc
---

# Системы авторизованного пользователя

* TOC
{:toc}

# Описание объекта "трекер" ("система") (?? Может отделить трекеры и автомобили ??)

|---
| Field name|Type|Required|Default value|Description|
| imei|string|true| - |Imei of the system
| phone | string|false| none| Telephone of the SIM-card
| default_voltage|float|false| 12|Normal car voltage
| type |enum (car, personal)|false|car| Type of the tracker
| car_info|link|false|none| Information for the car in this machine
| balance | float | false | 0 | Balance on the current account
| balance_currency|string|false|"USD"|Currency of the balance

# Действия

## Добавление системы

    POST /systems

### Запрос

<%= json :SYSTEM_create %>

### Ответ

<%= headers 201 %>
<%= json :SYSTEM_create %>
## Получение системы

    GET /systems/:imei

### Ответ

<%= headers 200 %>
<%= json :system %>
