# Авторизация

* TOC
{:toc}

## Вход или создание акаунта

    GET /login

### Запрос

username
: _Обязательный_ **string** - Имя пользователя

password
: _Обязательный_ **string** - Пароль

email
: _Необязательный_ **string** - Электронная почта

title
: _Необязательный_  **string** - Отображаемое имя

### Ответ

<%= headers 200 %>
<%= json :login %>


## Выход из акаунта

    GET /logout

### Ответ

<%= headers 200 %>
<%= json :result => "logout" %>

