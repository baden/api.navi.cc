# Авторизация

* TOC
{:toc}

## Вход в аккаунт

    GET /accounts/login

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



## Выход из акаунта

    POST /account/logout

### Ответ

<%= headers 204 %>


