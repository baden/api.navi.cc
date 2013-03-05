---
title: api.navi.cc API v1
---

# API v1

Это официальный документ для api.navi.cc версии 1.0. Если вы испытываете проблемы или имеете пожелания, пожалуйста свяжитесь с нами по адресу [support](mailto:baden.i.ua@gmail.com?subject=api.navi.cc_APIv1).

* TOC
{:toc}

## Схема

Все запросы начинаются с префикса `http://api.newgps.navi.cc/1.0`. Далее следует путь к ресурсу. Например, получить события, относящиеся к системе с ключом :skey можно по адресу `/logs/:skey`. Полный путь будет иметь вид:

<pre class="terminal">
$ curl -i http://api.newgps.navi.cc/1.0/logs/KEYFORSOMESYSTEM

HTTP/1.1 200 OK
Server: nginx
Date: Fri, 12 Oct 2012 23:33:14 GMT
Content-Type: application/json; charset=utf-8
Connection: keep-alive
Status: 200 OK
ETag: "a00049ba79152d03380c34652f2cb612"
Content-Length: 5
Cache-Control: max-age=0, private, must-revalidate

[]
</pre>

В большинстве запросов должен быть указан домен, с которого осуществляется запрос (CORS). Для этого должен быть установлен **Origin** в заголовке запроса.

<pre class="terminal">
$ curl -i http://api.newgps.navi.cc/1.0/info -H "Origin: http://some-site.com"
</pre>

В данный момент разрешены запросы с любого домена `Access-Control-Allow-Origin: *`, но нужно иметь ввиду, что в дальнейшем это может быть изменено.

Передаваемые и получаемые данные имеют JSON-формат.

## Параметры

Основные параметры являются частью пути запроса, далее запись вида `:value` подразумевает, что вместо `:value` необходимо подставить основной параметр, например в запросе `DELETE http://api.newgps.navi.cc/1.0/account/systems/:skey` вместо `:skey` необходимо указать ключ системы.

Большинство API-запросов могут содержать дополнительные параметры.

Для GET запросов, любые параметры, не являющиеся частью пути могут быть заданы в запросе:

<pre class="terminal">
$ curl -i http://api.newgps.navi.cc/1.0/info?verbose=yes&state=all
</pre>

Для POST-запроса, дополнительные параметры задаются в теле запроса. Если тело POST-запроса задано в JSON-формате, то должен быть установлен заголовок `Content-Type: application/json; charset=utf-8`.

<pre class="terminal">
$ curl -i -d '{"username":"baden","password":"333"}' http://api.newgps.navi.cc/1.0/login -H "Content-type: application/json;charset=UTF-8" -H "Origin: http://some-site.com"
</pre>

Если запрос содержит только строковые параметры, то в качестве альтернативы может использоватьcя `Content-Type: application/x-www-form-urlencoded`, но предпочтение отдается `application/json`:

<pre class="terminal">
$ curl -i http://api.newgps.navi.cc/1.0/login -d "username=baden&password=333" -H "Origin: http://some-site.com"
</pre>

## Ошибки

Если была попытка выполнения неавторизованного запроса, то будет возвращена ошибка:

        HTTP/1.1 401 Unauthorized
        Content-Type: application/json; charset=utf-8
        Content-Length: 68

        {
                "status_code": 401,
                "message": "Requires authentication"
        }

Пример возвращаемой ошибки при ошибке в параметрах:

        HTTP/1.1 400 Bad Request
        Content-Length: 69
        Content-Type: application/json; charset=utf-8

        {
                "status_code": 400,
                "message": "Problems parsing JSON"
        }

## HTTP-Методы

Там где это возможно, используются соответствующие HTTP-методы:

HEAD
: Can be issued against any resource to get just the HTTP header info.

GET
: Получение ресурса

DELETE
: Удаление ресурса

POST
: Создание ресурса или выполнение специальных действия над ресурсом.

PUT
: Замена ресурса

PATCH
: Обновления ресурса частичными данными из JSON-запроса.

## Авторизация

Для большинства запросов требуется авторизация. После выполнения запроса `/accounts/login` будет возвращен ключ авторизации token.

Доступны три способа авторизации запроса:

### Указание token как параметра запроса.

<pre class="terminal">
$ curl curl -i "http://api.newgps.navi.cc/1.0/account?token=TOKEN" -H "Origin: http://some-site.com"
</pre>

### Указание token в заголовке Authorization.

<pre class="terminal">
$ curl curl -i "http://api.newgps.navi.cc/1.0/account" -H "Origin: http://some-site.com" -H "X-Authorization: token"
</pre>

### Использование печенек.

Для запросов, поддерживающих `Access-Control-Allow-Credentials: true` будут установлены печеньки


## User Agent

Все запросы для корректной работы требуют чтобы был установлен `User Agent`.

## Формат основных ресурсов

### Базовые типы

string
: Строковое значение

number
: Числовое значение, в том числе значение с плавающей точкой.

integer
: Целочисленное числовое значение

boolean
: Булевое значение истина/ложь

object
: Значение тиап объект.

array
: Список значений. Список как правило содержит элементы одного типа, хотя это и не обязательно.

null
: Пустое значение. Применяется в случаях, когда необходимо чтобы поле существовало,
  но запись не содержала значения.

### Специальные типы

datetime
: Подвид типа **string**. Метка времени в формате ISO 8601: "YYYY-MM-DDTHH:MM:SSZ"

dt
: Подвит типа **integer**. Метка времени для данных, требующих особых условий хранения или передачи.
  Целочисленное значение. Дата/время указывается в Unux-time формате.
  Количество секунд, прошедших с полуночи (00:00:00 UTC) 1 января 1970 года (четверг).

key
: Подвит типа **string**. Ключ ресурса. Например, список наблюдаемых систем представляет собой
  запись типа **array** со значениями типа **key**.

any
: Значение может принимать любой тип из приведенных выше.



## Cross Origin Resource Sharing

API поддерживает Cross Origin Resource Sharing (CORS) для AJAX запросов.
Смотри [CORS W3C working draft](http://www.w3.org/TR/cors), или
[this intro](http://code.google.com/p/html5security/wiki/CrossOriginRequestSecurity).

Пример OPTIONS запроса через браузет с сайта `http://some-site.com`:

<pre class="terminal">
$ curl -i http://api.newgps.navi.cc/1.0/account -H "Origin: http://some-site.com" -X OPTIONS

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: http://some-site.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE
Access-Control-Allow-Headers: Authorization
...
</pre>

На данный момент поддерживаются запросы с любого домена. Домен представляет собой изолированную среду,
и может использоваться для создания сайта для компании. В которой могут быть свои пользователи, геозоны, маршруты, отчеты и т.п.

## JSON-P Callbacks

Можно указать параметр `?callback` для любого GET-запроса чтобы обрамить ответ в JSON функцию.

<pre class="terminal">
$ curl http://api.newgps.navi.cc?callback=foo

foo({
  "meta": {
    "status": 200
  },
  "data": {
    // the data
  }
})
</pre>


You can write a javascript handler to process the callback like this:

<pre class="highlight"><code class="language-javascript">function foo(response) {
  var meta = response.meta
  var data = response.data
  console.log(meta)
  console.log(data)
}</code></pre>



<%= json "Link" => [
  ["url1", {:rel => "next"}],
  ["url2", {:rel => "foo", :bar => "baz"}]] %>
