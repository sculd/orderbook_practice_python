from collections import defaultdict, deque
from sortedcontainers import SortedDict
import operator
import copy


class Order:
    new_id = 1
    def __init__(self, side, price, original_quantity, remaining_quantity):
        self.id = Order.new_id
        Order.new_id += 1
        self.side = side
        self.price = price
        self.original_quantity = original_quantity
        self.remaining_quantity = remaining_quantity
        self.cancelled = False

    def copy(self):
        return copy.copy(self)

    def __str__(self):
        return f"{self.id}, {self.side}, {self.price=}, {self.original_quantity=}, {self.remaining_quantity=}, {self.cancelled=}"


class OrderBook:
    def __init__(self):
        self.buy_orders_at_price = SortedDict()
        self.sell_orders_at_price = SortedDict()
        self.orders_id_to_order = {}

    def _get_best_price(self, side):
        if side == "buy":
            if not self.buy_orders_at_price:
                return None
            p, _ = self.buy_orders_at_price.peekitem(index=-1)
            return p
        else:
            if not self.sell_orders_at_price:
                return None
            p, _ = self.sell_orders_at_price.peekitem(index=0)
            return p

    def _append_new_order(self, side, price, quantity, remaining_quantity, orders_at_price):
        print(f"unmatched order {side=}, {price=}, {quantity=} {remaining_quantity=} being placed")
        order = Order(side, price, quantity, remaining_quantity)
        self.orders_id_to_order[order.id] = order
        if remaining_quantity > 0:
            print(f"unmatched order quantity {remaining_quantity=} being appended")
            orders_at_price.setdefault(price, deque()).append(order)
        return order.id

    def _match_order(self, price, quantity, side):
        if side == "buy":
            exit_comp, counter_orders_at_price, peek_index = operator.gt, self.sell_orders_at_price, 0
        else:
            exit_comp, counter_orders_at_price, peek_index = operator.lt, self.buy_orders_at_price, -1

        while counter_orders_at_price and quantity > 0:
            counter_price, counter_orders = counter_orders_at_price.peekitem(index=peek_index)
            if exit_comp(counter_price, price):
                break

            while counter_orders and quantity > 0:
                if counter_orders[0].cancelled:
                    counter_orders.popleft()
                elif quantity >= counter_orders[0].remaining_quantity:
                    print(f"remaining order {counter_orders[0]} being matched out")
                    quantity -= counter_orders[0].remaining_quantity
                    counter_orders[0].remaining_quantity = 0
                    counter_orders.popleft()
                else:
                    print(f"incoming order {price=}, {quantity=} being matched out")
                    counter_orders[0].remaining_quantity -= quantity
                    quantity = 0

            if not counter_orders:
                counter_orders_at_price.pop(counter_price)

        return quantity

    def add_order(self, side, price, quantity):
        remaining_quantity = self._match_order(price, quantity, side)
        if side == "buy":
            order_id = self._append_new_order(side, price, quantity, remaining_quantity, self.buy_orders_at_price)
        else:
            order_id = self._append_new_order(side, price, quantity, remaining_quantity, self.sell_orders_at_price)
        return order_id

    def cancel_order(self, order_id):
        order = self.orders_id_to_order[order_id]
        order.cancelled = True
        return order.copy()

    def get_order_status(self, order_id):
        return self.orders_id_to_order[order_id].copy()


class OrderManager:
    def __init__(self):
        self.orderbooks = defaultdict(OrderBook)
        self.orders_id_symbol = {}
    
    def add_order(self, symbol, side, price, quantity):
        order_id = self.orderbooks[symbol].add_order(side, price, quantity)
        self.orders_id_symbol[order_id] = symbol
        return order_id

    def cancel_order(self, order_id):
        return self.orderbooks[self.orders_id_symbol[order_id]].cancel_order(order_id)

    def get_order_status(self, order_id):
        return self.orderbooks[self.orders_id_symbol[order_id]].get_order_status(order_id)


def test_simple_nomatch():
    order_manager = OrderManager()
    order_manager.add_order("GOOG", "buy", 100, 10)
    order_manager.add_order("GOOG", "buy", 90, 20)
    order_manager.add_order("GOOG", "sell", 200, 10)

def test_simple_incoming_matched_out():
    order_manager = OrderManager()
    order_manager.add_order("GOOG", "buy", 100, 10)
    order_manager.add_order("GOOG", "buy", 90, 20)
    order_manager.add_order("GOOG", "sell", 80, 5)

def test_simple_remaining_matched_out():
    order_manager = OrderManager()
    id_b_0 = order_manager.add_order("GOOG", "buy", 100, 10)
    id_b_1 = order_manager.add_order("GOOG", "buy", 90, 20)
    id_s_0 = order_manager.add_order("GOOG", "sell", 80, 15)
    print(order_manager.get_order_status(id_b_0))
    print(order_manager.get_order_status(id_b_1))
    print(order_manager.get_order_status(id_s_0))

def test_simple_imcoming_sweepingout():
    order_manager = OrderManager()
    id_b_0 = order_manager.add_order("GOOG", "buy", 100, 10)
    id_b_1 = order_manager.add_order("GOOG", "buy", 90, 20)
    id_s_0 = order_manager.add_order("GOOG", "sell", 80, 40)
    print(order_manager.get_order_status(id_b_0))
    print(order_manager.get_order_status(id_b_1))
    print(order_manager.get_order_status(id_s_0))

def test_cancel_order():
    order_manager = OrderManager()
    id_b_0 = order_manager.add_order("GOOG", "buy", 100, 10)
    order_manager.cancel_order(id_b_0)
    id_b_1 = order_manager.add_order("GOOG", "buy", 90, 20)
    id_s_0 = order_manager.add_order("GOOG", "sell", 80, 15)
    print(order_manager.get_order_status(id_b_0))
    print(order_manager.get_order_status(id_b_1))
    print(order_manager.get_order_status(id_s_0))

if __name__ == "__main__":
    #test_simple_nomatch()
    #test_simple_incoming_matched_out()
    #test_simple_remaining_matched_out()
    test_simple_imcoming_sweepingout()
    #test_cancel_order()




