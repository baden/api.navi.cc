---
title: Account | api.navi.cc
---

# Аккаунт

* TOC
{:toc}

# Объект "стандартный аккаунт"


| Field name        | Type          | Required| Default value       |  Description
| username          | string        | true   | -                    | Account username
| password          | string        | true   | -                    | Account password
| email             | string        | false  | none                 | User email if was supplied
| title             | string        | false  | none                 | Displaying title
| created           | daytime       | false  | current_time         | Date of account creation
| roles             | array(string) | false  | user                 | Roles of the account  (only if account in corporation)
| systems           | object        | false  | -                    | All watched user systems
| default_timezone  | datetime      | false  | [ddr]]               | User default timezone
| time_format       | string        | false  | HH:MM:SS             | Displaying time format
| date_format       | string        | false  | DD-MM-YYYY           | Displaying date format
| datetime_format   | string        | false  | HH:MM:SS DD-MM-YYYY  | Displaying date and time format
| language          |string         | false  | [ddr]                | System language in full format "RU-ru", "EN-us"



**ddr -defined during registration**

## Создание аккаунта

    POST /accounts

#### Объект запроса

username
: _Обязательный_ **string** - Имя пользователя

password
: _Обязательный_ **string** - Пароль

email
: _Необязательный_ **string** - Электронная почта

title
: _Необязательный_  **string** - Отображаемое имя


### Ответ

<%= headers 201 %>
<%= json :login %>

Validation error
<%= headers 400 %>

## Вход в систему (Аутентификация пользователя)

    POST /accounts/login

В теле ответа содержится информация об акаунте и поле `token` которое необходимо для авторизации пользовательских действий [(детальнее)](/v0.1/#section-3).

### Объект запроса

username
: _Обязательный_ **string** - Имя пользователя

password
: _Обязательный_ **string** - Пароль

### Ответ

<%= headers 200 %>
<%= json :login %>

Wrong login or password

<%= error 403,:login_wr %>


Запросы при [авторизированном дочтупе](/v0.1/#authentication).

## Получение авторизованного аккаунта

    GET /account

Parameters:

* **detail_systems** - systems displayed like in [personal systems](../systems/)


### Ответ

<%= headers 200 %>
<%= json :full_account %>

## Обновление авторизованного аккаунта

    PATCH /account

### Запрос
<%= json :title => "new title" %>

### Ответ

<%= headers 204 %>

## Удаление аккаунта

    DELETE /account

### Ответ

<%= headers 204 %>

## Выход из системы

    POST /account/logout

### Ответ

<%= headers 204 %>
