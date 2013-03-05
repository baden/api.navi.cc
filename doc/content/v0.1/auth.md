# Авторизация

* TOC
{:toc}

## Вход в аккаунт

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





