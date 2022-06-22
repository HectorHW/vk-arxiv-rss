# постер для arxiv.pl

Бот, который постит ссылки на статьи из RSS arxiv.PL в группу вк

## авторизация

Создайте приложение, скопируйте его id в ссылку ниже:

```url
https://oauth.vk.com/authorize?client_id=<YOUR ID HERE>&scope=wall,offline,groups&response_type=token
```

Перейдите по ней, выдайте разрешения, скопируйте `access_token`

## Конфигурация

Полученный токен вставьте в `config.py`. Туда же запишите id группы и (при необходимости) интервал проверки
