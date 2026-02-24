scetch_quest_json = {
      "categories": [
        {
          "name": "Заказ скетча",
          "questions": [
              {
                "text": "Как к вам обращаться?",
                "type": "text",
                "required": "true",
                "placeholder": "",
                "db_field": "name",
                "state": "ask_name"
              },
              {
                "text": "Номер телефона для связи?",
                "type": "phone",
                "required": "true",
                "placeholder": "10 цифр без 8 и +7 в начале",
                "db_field": "phone",
                "state": "ask_phone"
              },
              {
                "text": "Ник в телеграм",
                "type": "text",
                "required": "true",
                "placeholder": "",
                "db_field": "tg_nick",
                "state": "ask_nickname"
              },
              {
                "text": "Ваш Email?",
                "type": "email",
                "required": "false",
                "placeholder": "В формате abs@def.gh",
                "db_field": "email",
                "state": "ask_email"
              },
              {
                "text": "Дата мероприятия:",
                "type": "text",
                "required": "true",
                "placeholder": "",
                "db_field": "event_date",
                "state": "ask_date"
              },
              {
                "text": "Какой формат картинки вы хотите?",
                "type": "scetch_variant",
                "required": "true",
                "placeholder": "",
                "db_field": "scetch_variant",
                "state": "ask_variant"
              },
              {
                "text": "Количество часов?",
                "type": "number",
                "required": "true",
                "placeholder": "",
                "db_field": "hours_qty",
                "state": "ask_hours_qty"
              },
              {
                "text": "Примерное время начала?",
                "type": "text",
                "required": "true",
                "placeholder": "",
                "db_field": "start_time",
                "state": "ask_time"
              },
              {
                "text": "Адрес мероприятия:",
                "type": "text",
                "required": "true",
                "placeholder": "",
                "db_field": "address",
                "state": "ask_address"
              }
          ]
        },
        {
          "name": "Контакты",
          "questions": [
            {
              "text": "Email?",
              "type": "email",
              "required": "false",
              "db_field": "email",
              "state": "ask_email"
            },
            {
              "text": "Телефон?",
              "type": "phone",
              "required": "true",
              "db_field": "phone",
              "state": "ask_phone"
            }
          ]
        }
      ]
}