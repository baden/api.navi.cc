---
title: Account | api.navi.cc
---

# Аккаунт

* TOC
{:toc}

Большинство запросов работают с [авторизованным аккаунтом](/v3/#authentication).
Такие запросы не содержат параметр `:akey`.

## Получение авторизованного аккаунта

    GET /account

### Ответ

<%= headers 200 %>
<%= json :full_account %>

## Обновление авторизованного аккаунта

    PATCH /account

### Запрос

title
: _Optional_ **string**

email
: _Optional_ **string** - Publicly visible email address.

company
: _Optional_ **string**

location
: _Optional_ **string**


<%= json \
    :title    => "Денис",
    :email    => "denis@batrak.com",
    :company  => "NaviCC",
    :location => "Днепропетровск"
%>

### Ответ

<%= headers 200 %>
<%= json :full_account %>

