---
title: Системы пользователя | api.navi.cc
---

# Системы авторизованного пользователя

* TOC
{:toc}

# Описание трекера, привязанного к пользователю

|---
| Field name|Type|Required|Default value|Description|
| imei|string|true| - |Imei of the system
| title | string|false| none| Tetle fot this system
| icon | string|false| none| Name of the predefined icon
| track_color | string|false| none| Color of the track in hexedecimal format (RRGGBB)
| groups| array[string] | false| none| Groups for this system


# Действия

## Добавление системы в список пользователя

    POST /account/systems

### Запрос

<%= json :user_system_create  %>

### Ответ

<%= headers 201 %>
<%= json :system %>

## Получение всех системы

    GET /account/systems


Необходимо наличие дочтаточной информации для отображения карты

### Ответ

<%= headers 200 %>
<%= json :all_user_systems %>

## Изменение порядка наблюдаемых систем

    POST /account/systems/sort

### Запрос
IMEI в новом порядке

<%= json ["IMEI1", "IMEI2", "IMEI3"] %>

### Ответ

<%= headers 204 %>


## Удаление системы из списка наблюдения

    DELETE /account/systems/:imei

### Ответ

<%= headers 204 %>

