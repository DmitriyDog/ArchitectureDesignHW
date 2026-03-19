from abc import ABC, abstractmethod
from typing import List, Optional
import threading

# ======================== ПОРОЖДАЮЩИЕ ШАБЛОНЫ (CREATIONAL) ========================

# 1. Singleton - Одиночка (управление подключением к базе данных)
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.connection_string = "postgresql://localhost:5432/restaurant"
                    print(f"Создание подключения к БД: {cls._instance.connection_string}")
        return cls._instance

    def query(self, sql: str):
        print(f"Выполнение запроса: {sql}")

# 2. Factory Method - Фабричный метод (создание разных типов блюд)
class Dish(ABC):
    @abstractmethod
    def prepare(self):
        pass
    
    @abstractmethod
    def serve(self):
        pass

class Pizza(Dish):
    def prepare(self):
        print("Готовим пиццу: замес теста, добавление начинки")
    
    def serve(self):
        print("Подаем пиццу на круглой тарелке")

class Pasta(Dish):
    def prepare(self):
        print("Готовим пасту: варка макарон, приготовление соуса")
    
    def serve(self):
        print("Подаем пасту в глубокой тарелке")

class Salad(Dish):
    def prepare(self):
        print("Готовим салат: нарезка овощей, заправка")
    
    def serve(self):
        print("Подаем салат в большой миске")

class DishFactory(ABC):
    @abstractmethod
    def create_dish(self) -> Dish:
        pass
    
    def order_dish(self) -> Dish:
        dish = self.create_dish()
        dish.prepare()
        dish.serve()
        return dish

class PizzaFactory(DishFactory):
    def create_dish(self) -> Dish:
        return Pizza()

class PastaFactory(DishFactory):
    def create_dish(self) -> Dish:
        return Pasta()

class SaladFactory(DishFactory):
    def create_dish(self) -> Dish:
        return Salad()

# 3. Builder - Строитель (конструирование сложного заказа)
class Order:
    def __init__(self, builder):
        self.dishes = builder.dishes
        self.customer_name = builder.customer_name
        self.delivery_address = builder.delivery_address
        self.is_takeaway = builder.is_takeaway
        self.special_instructions = builder.special_instructions
    
    def display_order(self):
        print(f"Заказ для: {self.customer_name}")
        print(f"Блюда: {len(self.dishes)}")
        print(f"На вынос: {'Да' if self.is_takeaway else 'Нет'}")
        if self.delivery_address:
            print(f"Адрес: {self.delivery_address}")
        if self.special_instructions:
            print(f"Особые пожелания: {self.special_instructions}")
    
    class OrderBuilder:
        def __init__(self, customer_name: str):
            self.customer_name = customer_name
            self.dishes = []
            self.delivery_address = None
            self.is_takeaway = False
            self.special_instructions = None
        
        def add_dish(self, dish: Dish):
            self.dishes.append(dish)
            return self
        
        def set_delivery_address(self, address: str):
            self.delivery_address = address
            self.is_takeaway = False
            return self
        
        def set_takeaway(self):
            self.is_takeaway = True
            self.delivery_address = None
            return self
        
        def set_special_instructions(self, instructions: str):
            self.special_instructions = instructions
            return self
        
        def build(self):
            return Order(self)

# ======================== СТРУКТУРНЫЕ ШАБЛОНЫ (STRUCTURAL) ========================

# 1. Adapter - Адаптер (для интеграции со сторонней системой оплаты)
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float):
        pass

class InternalPaymentSystem:
    def make_transaction(self, amount: float):
        print(f"Внутренняя система: обработка платежа на сумму {amount}")

class ExternalPaymentGateway:
    def send_payment_request(self, amount: float, currency: str):
        print(f"Внешний шлюз: запрос на оплату {amount} {currency}")

class ExternalPaymentAdapter(PaymentProcessor):
    def __init__(self, external_gateway: ExternalPaymentGateway):
        self.external_gateway = external_gateway
    
    def process_payment(self, amount: float):
        self.external_gateway.send_payment_request(amount, "RUB")

# 2. Decorator - Декоратор (добавление дополнений к блюдам)
class MenuItem(ABC):
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_price(self) -> float:
        pass

class BaseDish(MenuItem):
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
    
    def get_description(self) -> str:
        return self.name
    
    def get_price(self) -> float:
        return self.price

class DishDecorator(MenuItem):
    def __init__(self, decorated_dish: MenuItem):
        self.decorated_dish = decorated_dish
    
    def get_description(self) -> str:
        return self.decorated_dish.get_description()
    
    def get_price(self) -> float:
        return self.decorated_dish.get_price()

class ExtraCheese(DishDecorator):
    def get_description(self) -> str:
        return f"{self.decorated_dish.get_description()} + сыр"
    
    def get_price(self) -> float:
        return self.decorated_dish.get_price() + 50.0

class ExtraBacon(DishDecorator):
    def get_description(self) -> str:
        return f"{self.decorated_dish.get_description()} + бекон"
    
    def get_price(self) -> float:
        return self.decorated_dish.get_price() + 80.0

# 3. Facade - Фасад (упрощенный интерфейс для работы с кухней)
class KitchenFacade:
    def __init__(self):
        self.pizza_factory = PizzaFactory()
        self.pasta_factory = PastaFactory()
        self.salad_factory = SaladFactory()
        self.prepared_dishes = []
    
    def prepare_full_meal(self):
        print("=== Приготовление комплексного обеда ===")
        self.prepared_dishes.append(self.pizza_factory.create_dish())
        self.prepared_dishes.append(self.pasta_factory.create_dish())
        self.prepared_dishes.append(self.salad_factory.create_dish())
    
    def prepare_pizza_meal(self):
        print("=== Пицца-комбо ===")
        self.prepared_dishes.append(self.pizza_factory.create_dish())
        self.prepared_dishes.append(self.salad_factory.create_dish())
    
    def get_prepared_dishes(self):
        return self.prepared_dishes

# 4. Composite - Компоновщик (группировка блюд в комбо-наборы)
class MenuComponent(ABC):
    @abstractmethod
    def display(self):
        pass
    
    @abstractmethod
    def get_price(self) -> float:
        pass

class MenuItemLeaf(MenuComponent):
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
    
    def display(self):
        print(f" - {self.name}: {self.price} руб.")
    
    def get_price(self) -> float:
        return self.price

class MenuComposite(MenuComponent):
    def __init__(self, name: str):
        self.name = name
        self.components = []
    
    def add_component(self, component: MenuComponent):
        self.components.append(component)
    
    def remove_component(self, component: MenuComponent):
        self.components.remove(component)
    
    def display(self):
        print(f"{self.name} (комбо):")
        for component in self.components:
            component.display()
    
    def get_price(self) -> float:
        return sum(component.get_price() for component in self.components)

# ======================== ПОВЕДЕНЧЕСКИЕ ШАБЛОНЫ (BEHAVIORAL) ========================

# 1. Observer - Наблюдатель (уведомление о готовности заказа)
class OrderObserver(ABC):
    @abstractmethod
    def update(self, order_status: str):
        pass

class Customer(OrderObserver):
    def __init__(self, name: str):
        self.name = name
    
    def update(self, order_status: str):
        print(f"Уважаемый {self.name}, статус вашего заказа: {order_status}")

class KitchenStaff(OrderObserver):
    def __init__(self, name: str):
        self.name = name
    
    def update(self, order_status: str):
        print(f"Повар {self.name}, заказ {order_status}")

class OrderSubject:
    def __init__(self):
        self._observers = []
        self._order_status = ""
    
    def attach(self, observer: OrderObserver):
        self._observers.append(observer)
    
    def detach(self, observer: OrderObserver):
        self._observers.remove(observer)
    
    @property
    def order_status(self):
        return self._order_status
    
    @order_status.setter
    def order_status(self, status: str):
        self._order_status = status
        self._notify_observers()
    
    def _notify_observers(self):
        for observer in self._observers:
            observer.update(self._order_status)

# 2. Strategy - Стратегия (разные способы расчета стоимости)
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_price: float) -> float:
        pass

class RegularPricing(PricingStrategy):
    def calculate_price(self, base_price: float) -> float:
        return base_price

class DiscountPricing(PricingStrategy):
    def __init__(self, discount_percent: float):
        self.discount_percent = discount_percent
    
    def calculate_price(self, base_price: float) -> float:
        return base_price * (1 - self.discount_percent / 100)

class LoyaltyPricing(PricingStrategy):
    def calculate_price(self, base_price: float) -> float:
        return base_price * 0.9  # 10% скидка постоянным клиентам

# 3. Command - Команда (инкапсуляция запросов к кухне)
class KitchenCommand(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class PrepareDishCommand(KitchenCommand):
    def __init__(self, chef, dish_name: str):
        self.chef = chef
        self.dish_name = dish_name
    
    def execute(self):
        self.chef.cook_dish(self.dish_name)
    
    def undo(self):
        self.chef.cancel_dish(self.dish_name)

class Chef:
    def __init__(self, name: str):
        self.name = name
    
    def cook_dish(self, dish_name: str):
        print(f"Шеф-повар {self.name} готовит: {dish_name}")
    
    def cancel_dish(self, dish_name: str):
        print(f"Шеф-повар {self.name} отменяет: {dish_name}")

# 4. Chain of Responsibility - Цепочка обязанностей (обработка заказа)
class OrderHandler(ABC):
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler):
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, order: Order):
        if self._next_handler:
            self._next_handler.handle(order)

class ValidationHandler(OrderHandler):
    def handle(self, order: Order):
        print("Валидация заказа...")
        if order:
            print("Заказ прошел валидацию")
            super().handle(order)

class CookingHandler(OrderHandler):
    def handle(self, order: Order):
        print("Передача заказа на кухню...")
        print("Приготовление заказа...")
        super().handle(order)

class DeliveryHandler(OrderHandler):
    def handle(self, order: Order):
        print("Передача заказа в службу доставки...")
        print("Заказ доставлен клиенту")

# 5. State - Состояние (статусы заказа)
class OrderState(ABC):
    @abstractmethod
    def next(self, context):
        pass
    
    @abstractmethod
    def prev(self, context):
        pass
    
    @abstractmethod
    def print_status(self):
        pass

class NewOrderState(OrderState):
    def next(self, context):
        context.state = CookingState()
    
    def prev(self, context):
        print("Заказ уже в начальном состоянии")
    
    def print_status(self):
        print("Статус: Новый заказ принят")

class CookingState(OrderState):
    def next(self, context):
        context.state = ReadyState()
    
    def prev(self, context):
        context.state = NewOrderState()
    
    def print_status(self):
        print("Статус: Готовится на кухне")

class ReadyState(OrderState):
    def next(self, context):
        context.state = DeliveredState()
    
    def prev(self, context):
        context.state = CookingState()
    
    def print_status(self):
        print("Статус: Заказ готов к выдаче")

class DeliveredState(OrderState):
    def next(self, context):
        print("Заказ уже доставлен")
    
    def prev(self, context):
        context.state = ReadyState()
    
    def print_status(self):
        print("Статус: Заказ доставлен")

class OrderContext:
    def __init__(self):
        self._state = NewOrderState()
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state: OrderState):
        self._state = state
    
    def next_state(self):
        self._state.next(self)
    
    def prev_state(self):
        self._state.prev(self)
    
    def print_status(self):
        self._state.print_status()

# ======================== ДЕМОНСТРАЦИЯ РАБОТЫ ========================
def main():
    print("=== СИСТЕМА УПРАВЛЕНИЯ РЕСТОРАНОМ ===\n")
    
    # Демонстрация порождающих шаблонов
    print("--- ПОРОЖДАЮЩИЕ ШАБЛОНЫ ---")
    
    # Singleton
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(f"db1 и db2 - один объект? {db1 is db2}")
    
    # Factory Method
    pizza_factory = PizzaFactory()
    pizza = pizza_factory.order_dish()
    
    # Builder
    order = Order.OrderBuilder("Иван Петров")\
        .add_dish(Pizza())\
        .add_dish(Salad())\
        .set_delivery_address("ул. Ленина, д.10")\
        .set_special_instructions("Без лука")\
        .build()
    order.display_order()
    
    # Демонстрация структурных шаблонов
    print("\n--- СТРУКТУРНЫЕ ШАБЛОНЫ ---")
    
    # Adapter
    processor = ExternalPaymentAdapter(ExternalPaymentGateway())
    processor.process_payment(1500.0)
    
    # Decorator
    pizza_base = BaseDish("Пицца Маргарита", 450.0)
    pizza_with_cheese = ExtraCheese(pizza_base)
    pizza_with_cheese_and_bacon = ExtraBacon(pizza_with_cheese)
    print(f"{pizza_with_cheese_and_bacon.get_description()} стоит: {pizza_with_cheese_and_bacon.get_price()}")
    
    # Facade
    kitchen = KitchenFacade()
    kitchen.prepare_full_meal()
    
    # Composite
    combo_meal = MenuComposite("Бизнес-ланч")
    combo_meal.add_component(MenuItemLeaf("Суп", 150.0))
    combo_meal.add_component(MenuItemLeaf("Горячее", 250.0))
    combo_meal.add_component(MenuItemLeaf("Салат", 100.0))
    combo_meal.display()
    print(f"Итого: {combo_meal.get_price()}")
    
    # Демонстрация поведенческих шаблонов
    print("\n--- ПОВЕДЕНЧЕСКИЕ ШАБЛОНЫ ---")
    
    # Observer
    subject = OrderSubject()
    customer = Customer("Анна")
    staff = KitchenStaff("Мария")
    subject.attach(customer)
    subject.attach(staff)
    subject.order_status = "Готовится"
    subject.order_status = "Готов к выдаче"
    
    # Strategy
    regular = RegularPricing()
    discount = DiscountPricing(10)
    print(f"Обычная цена: {regular.calculate_price(1000)}")
    print(f"Со скидкой: {discount.calculate_price(1000)}")
    
    # Command
    chef = Chef("Алексей")
    command = PrepareDishCommand(chef, "Паста Карбонара")
    command.execute()
    command.undo()
    
    # Chain of Responsibility
    validation = ValidationHandler()
    cooking = CookingHandler()
    delivery = DeliveryHandler()
    
    validation.set_next(cooking).set_next(delivery)
    validation.handle(order)
    
    # State
    order_context = OrderContext()
    order_context.print_status()
    order_context.next_state()
    order_context.print_status()
    order_context.next_state()
    order_context.print_status()
    order_context.next_state()
    order_context.print_status()

if __name__ == "__main__":
    main()
