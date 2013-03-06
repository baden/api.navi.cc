---
title: User account
---
#<%= @item[:title] %>

Standart user accaunt in system.

#Contents
* TOC
{:toc}

## Объект "стандартный аккаунт" # {#obj}

|-------------------+---------------+----------------------+--------------------------------------------------|
| Field name        | Type          | Default value        |  Description                                     |
|-------------------|---------------|----------------------|--------------------------------------------------|
| username          | string        | -                    | Account username                                 |
| password          | string        | -                    | Account password                                 |
| email             | string        | none                 | User email if was supplied                       |
| title             | string        | none                 | Displaying title                                 |
| created           | daytime       | current_time         | Date of account creation                         |
| roles             | array(string) | user                 | Roles of the account  (only if account in corporation)
| systems           | object        | -                    | All watched user systems                         |
| default_timezone  | datetime      | [ddr]                | User default timezone                            |
| time_format       | string        | HH:MM:SS             | Displaying time format                           |
| date_format       | string        | DD-MM-YYYY           | Displaying date format                           |
| datetime_format   | string        | HH:MM:SS DD-MM-YYYY  | Displaying date and time format                  |
| language          | string        | [ddr]                | System language in full format "RU-ru", "EN-us"  |
|-------------------+---------------+----------------------+--------------------------------------------------|

*ddr -defined during registration*

## Создание аккаунта {#create}

    POST /accounts

Обязательные параметры запроса: [`username`](#obj), [`password`](#obj)

### Запрос

<%= json(:username => "my_name", :password => "my_long_password", :email => "mail@example.com") %>

### Ответ

<%= headers 201 %>
<%= json :login %>

## Вход в систему (Аутентификация пользователя) {#login}

    POST /accounts/login

Обязательные параметры запроса: [`username`](#obj), [`password`](#obj)

В теле ответа содержится информация об акаунте и поле `token` которое необходимо для авторизации пользовательских действий [(детальнее)](/v0.1/#section-3).

### Запрос

<%= json :username => "my_name", :password => "my_long_password" %>

### Ответ

<%= headers 200 %>
<%= json :login %>

Wrong login or password

<%= error 403,:login_wr %>


Запросы при [авторизированном доступе](/v0.1/#authentication).

## Получение авторизованного аккаунта {#read}

    GET /account

Parameters:

* **detail_systems** - systems displayed like in [personal systems](../systems/)


### Ответ

<%= headers 200 %>
<%= json :full_account %>

## Обновление авторизованного аккаунта {#update}

    PATCH /account

### Запрос

<%= json :title => "new title" %>

### Ответ

<%= headers 204 %>

## Удаление аккаунта {#delete}

    DELETE /account

### Ответ

<%= headers 204 %>

## Выход из системы {#logout}

    POST /account/logout

### Ответ

<%= headers 204 %>