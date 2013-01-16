---
title: Системы пользователя | api.navi.cc
---

# Системы авторизованного пользователя

* TOC
{:toc}

## Добавление системы

    POST /account/systems

### Запрос

<%= json :cmd => "add", :imeis => ["IMEI1", "IMEI2", "IMEI3"] %>

### Ответ

<%= headers 201, :Location => "http://api.navi.cc/account/systems/*" %>
<%= json :systems %>

## Изменение порядка наблюдаемых систем

    POST /account/systems

### Запрос

<%= json :cmd => "sort", :skeys => ["SKEY3", "SKEY2", "SKEY1"] %>

### Ответ

<%= headers 200 %>
<%= json :skeys => ["SKEY3", "SKEY2", "SKEY1"] %>

## Удаление системы из списка наблюдения

    DELETE /account/systems/:skey

### Ответ

<%= headers 204 %>
