# from decimal import Decimal
# from django.shortcuts import get_object_or_404
# from main.models import Product
#
#
# class Cart:
#     def __init__(self, request):
#         self.session = request.session # получаем объект сессии из запроса
#
#         if not (cart := self.session.get('cart')):
#             cart = self.session['cart'] = {} # создаём пустую корзину в сессии
#         self.cart = cart                     # сохраняем ссылку на словарь корзины
#
#     def add(self, product, size, quantity=1, override_quantity=False):
#         product_id = str(product.id)
#         size_name = str(size)
#         cart_key = f"{product_id}_{size_name}"
#
#         if cart_key not in self.cart:
#             self.cart[cart_key] = {
#                 'quantity': 0,
#                 'price': str(product.price),
#                 'product_id': product.id,
#                 'size': size_name,
#             }
#
#         if override_quantity:
#             self.cart[cart_key]['quantity'] = override_quantity
#         else:
#             self.cart[cart_key]['quantity'] += quantity
#
#         self.save()
#
#     def save(self):
#         self.session.modified = True
#
#     def remove(self, product, size):
#         product_id = str(product.id)
#         size_name = str(size)
#         cart_key = f"{product_id}_{size_name}"
#
#         if cart_key in self.cart:
#             del self.cart[cart_key]
#             self.save()
#
#     def update_quantity(self, product, size, quantity):
#         product_id = str(product.id)
#         size_name = str(size)
#         cart_key = f"{product_id}_{size_name}"
#
#         if cart_key in self.cart:
#             if quantity <= 0:
#                 self.remove(product, size)
#             else:
#                 self.add(product, size, quantity, override_quantity=True)
#
#     def __iter__(self):
#         product_ids = [i['product_id'] for i in self.cart.values()]
#         products = Product.objects.filter(id__in=product_ids)
#         cart = self.cart.copy()
#
#         for product in products:
#             for cart_key, cart_item in cart.items():
#                 if cart_item['product_id'] == str(product.id):
#                     cart_item['product'] = product
#                     cart_item['total_price'] = Decimal(product.price * cart_item['quantity'])
#                     yield cart_item
#
#     def __len__(self):
#         length = sum(i['quantity'] for i in self.cart.values())
#         return length
#
#     def get_total_price(self):
#         total_price = sum(Decimal(i['price'] * i['quantity']) for i in self.cart.values())
#         return total_price
#
#     def clear(self):
#         del self.session['cart']
#         self.save()
#
#     def get_cart_items(self):
#         items = []
#         for i in self:
#             items.append({
#                 'product': i['product'],
#                 'quantity': i['quantity'],
#                 'size': i['size'],
#                 'price': Decimal(i['price']),
#                 'total_price': Decimal(i['total_price']),
#                 'cart_key': f"{i['product_id']}_{i['size']}",
#             })
#         return items
