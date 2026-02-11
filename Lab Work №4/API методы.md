## 1. Принятые проектные решения
### 1.1. Идентификаторы ресурсов в формате UUID
Решение: Все идентификаторы товаров, категорий и транзакций используют UUID.
Обоснование: Миллионы+ пользователей и возможность создания пользовательского контента (кастомные предметы) исключают использование автоинкрементных ID из-за риска коллизий и необходимости централизованной координации.

### 1.2. Пагинация на основе последнего полученного элемента
Решение: Для эндпоинтов, возвращающих списки (каталог, инвентарь), используется cursor-based пагинация, а не offset/limit, где курсор - это закодированная информация о последненм полученном элементе.
Обоснование: Высокий приоритет производительности. Курсорная пагинация стабильно работает на больших объемах данных и избегает проблемы пропуска/дублирования записей при сдвиге offset.  
Например, запрос SELECT * FROM catalog ORDER BY id LIMIT 20 OFFSET 1000000; читает первые 1000000 строк и затем еще 20, отчего запросы становятся значительно медленнее.
В то время как SELECT * FROM catalog WHERE id > 'последний-увиденный-id' ORDER BY id LIMIT 20; примерно одинаковую скорость для любой страницы.
Таким образом решается еще одна проблема, когда пагинация "съезжает", если между запросами страниц товар был удален или добавлен.

### 1.3. Использование стандартных кодов ошибок
Решение: API строго использует стандартные HTTP-коды статуса для обозначения результата операции, а не маскирует ошибки под 200 OK с флагом success: false в теле ответа.  
Обоснование: используем HTTP-коды по их прямому назначению. 2xx — успех,
4xx — вина клиента, 5xx — проблема сервера. Это повышает наблюдаемость системы и упрощает разработку клиентов, что критически важно при миллионах пользователей.

### 1.4. Идемпотентность для POST /purchases
Решение: Клиент обязан передать уникальный идентификатор операции (UUID) в заголовке Idempotency-Key.  
Алгоритм:  
1. Получили запрос с ключом K  
2. Проверили в Redis/БД: выполняли ли мы операцию с ключом K?  
3. Если нет — выполняем покупку, сохраняем результат под ключом K  
4. Если да — немедленно возвращаем сохраненный результат

Обоснование: из-за нестабильного интернет соединения могут происходит повторные события покупки у одного игрока (пользователь нажал "Купить" в магазине, операция загружалась,
появилась ошибка в самом магазине или браузере, игрок нажал "Купить" еще раз, через минуту в инвентаре игрока оказалось 2 предмета и деньги списались 2 раза, а не 1). 

### 1.5. Версионирование через URL
Решение: Версия API указывается непосредственно в пути URL.
Обосонование: простота использования, возможность постепенной миграции клиентов (старые клиенты используют /v1/, новые клиенты - /v2/)

### 1.6. Расширения запросов через fields-параметр
Решение: Клиент может запросить только необходимые поля ресурса: GET /catalog?fields=id,name,price.
Обоснование: Экономия трафика и ускорение сериализации на сервере. Особенно актуально для мобильных браузеров и медленных соединений.

### 1.7. ISO 8601 для временных меток
Решение: Все даты и время передаются в формате ISO 8601 (UTC).
Обоснование: Глобальная аудитория. Исключение ошибок, связанных с часовыми поясами.

### 1.8. Проблема N+1 запроса при работе с инвентарем
Решение: Эндпоинт GET /inventory/items поддерживает параметр expand для включения в ответ детальной информации о предмете (описание, иконка).
Обоснование: Типичный паттерн: получить список ID предметов игрока, затем запросить каждый предмет. Параметр expand позволяет получить всё за 1 запрос.

## 2. API эндпоинты
### 2.1. GET /items-store  
Получение каталога товаров с фильтрацией и пагинацией.  

Параметры запроса:  
cursor - курсор следующей страницы  
limit - лимит записей (1-100)  
type - фильтр по типу (skin, weapon, ...)  
rarity - фильтр по редкости  
search - поиск по названию  
fields - список запрашиваемых полей  
Ответы: 200 OK  

Запрос:  
<img width="1074" height="1131" alt="image" src="https://github.com/user-attachments/assets/89da4493-bf4d-499a-ac98-d33adf737693" />
<img width="841" height="503" alt="image" src="https://github.com/user-attachments/assets/d020daa7-4a0a-4b9a-a9ac-2b6f06417036" />



Код автотестов:  
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has items array", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.items).to.be.an('array');
});

pm.test("Save first item ID to variable", function () {
    const jsonData = pm.response.json();
    if (jsonData.items.length > 0) {
        pm.environment.set("itemId", jsonData.items[0].id);
    }
});
```

### 2.2. GET /catalog/{itemId}
Получение детальной информации о конкретном товаре.

Ответы: 200 OK / 404 Not Found
<img width="1029" height="1087" alt="image" src="https://github.com/user-attachments/assets/ede46e3b-0691-42da-93b1-91c36d3218be" />
<img width="872" height="496" alt="image" src="https://github.com/user-attachments/assets/b562929a-5208-4678-9c16-541c0347247a" />



Код автотестов:  
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Item ID matches requested", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.id).to.equal(pm.environment.get("itemId"));
});

pm.test("Item has name and price", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.name).to.be.a('string');
    pm.expect(jsonData.price.amount).to.be.a('number');
});
```

### 2.3. POST /purchases
Оформление покупки товара.

<img width="1057" height="321" alt="image" src="https://github.com/user-attachments/assets/ad8a83f7-a98e-45e7-9d8e-f537c0fb037b" />
<img width="707" height="408" alt="image" src="https://github.com/user-attachments/assets/057e433a-06f9-43e7-966d-53e1550a2d2f" />


Код автотестов:  
```js
pm.test("Status code is 201 Created", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has transactionId", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.transactionId).to.be.a('string');
    pm.expect(jsonData.status).to.equal('success');
    pm.environment.set("transactionId", jsonData.transactionId);
    pm.environment.set("instanceId", jsonData.itemInstanceId);
});
```

### 2.4. GET /purchases/{transactionId}
Получение статуса транзакции покупки.  
Ответы: 200 OK / 404 Not Found  
<img width="1105" height="1059" alt="image" src="https://github.com/user-attachments/assets/e6261c9a-4035-4e73-a577-b9d90e888f55" />
<img width="896" height="485" alt="image" src="https://github.com/user-attachments/assets/f1ede100-5c52-4596-9eb7-6823cb152f14" />

Код автотестов:  
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Transaction status is success", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal('success');
    pm.expect(jsonData.transactionId).to.equal(pm.environment.get("transactionId"));
});
```

### 2.5. GET /inventory/items
Получение инвентаря текущего игрока.

Параметры: cursor, limit, equipped (boolean), expand (включает детали предмета)  
Ответы: 200 OK
<img width="1105" height="1059" alt="image" src="https://github.com/user-attachments/assets/57bc16a6-4a4d-4a2b-85df-a7bf0d9ab674" />


Код автотестов:  
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Inventory has items", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.items).to.be.an('array');
});

pm.test("Item details are expanded", function () {
    const jsonData = pm.response.json();
    if (jsonData.items.length > 0) {
        pm.expect(jsonData.items[0].itemDetails).to.be.an('object');
    }
});
```

### 2.6. PUT /inventory/items/{instanceId}/equip
Экипировка предмета из инвентаря.  

Ответы: 200 OK
<img width="1043" height="325" alt="image" src="https://github.com/user-attachments/assets/8d353cf2-993a-42e3-8189-1c645b2756f8" />
<img width="996" height="474" alt="image" src="https://github.com/user-attachments/assets/d9eaff05-23fe-4c56-b8f6-f1f2d966545e" />
<img width="849" height="459" alt="image" src="https://github.com/user-attachments/assets/5d224928-aba4-4b6e-9934-f8145652b5cd" />



Код автотестов:  
```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Item equipped successfully", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.equipped).to.equal(true);
    pm.expect(jsonData.instanceId).to.equal(pm.environment.get("instanceId"));
});
```
