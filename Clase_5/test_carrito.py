import pytest
from carrito import Producto, Carrito


def test_crear_producto_valido():
    producto = Producto("Teclado", 15000, 2)
    assert producto.nombre == "Teclado"
    assert producto.precio == 15000
    assert producto.cantidad == 2


def test_subtotal_producto():
    producto = Producto("Mouse", 8000, 3)
    assert producto.subtotal() == 24000


def test_producto_sin_nombre():
    with pytest.raises(ValueError):
        Producto("", 1000, 1)


def test_precio_negativo():
    with pytest.raises(ValueError):
        Producto("Monitor", -5000, 1)


def test_cantidad_invalida():
    with pytest.raises(ValueError):
        Producto("Cable", 1000, 0)


def test_agregar_producto_al_carrito():
    carrito = Carrito()
    producto = Producto("Laptop", 500000, 1)
    carrito.agregar_producto(producto)

    assert len(carrito.productos) == 1


def test_eliminar_producto_existente():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Teclado", 15000, 1))
    carrito.agregar_producto(Producto("Mouse", 8000, 1))

    carrito.eliminar_producto("Teclado")

    assert len(carrito.productos) == 1
    assert carrito.productos[0].nombre == "Mouse"


def test_eliminar_producto_ignora_mayusculas_y_espacios():
    carrito = Carrito()
    carrito.agregar_producto(Producto("  Monitor  ", 120000, 1))

    carrito.eliminar_producto("monitor")

    assert len(carrito.productos) == 0


def test_eliminar_producto_inexistente_lanza_error():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Silla", 50000, 1))

    with pytest.raises(ValueError, match="El producto no se encuentra en el carrito"):
        carrito.eliminar_producto("Mesa")


def test_total_carrito():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Teclado", 15000, 2))
    carrito.agregar_producto(Producto("Mouse", 8000, 1))

    assert carrito.total() == 38000


def test_aplicar_descuento():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Silla", 100000, 1))

    assert carrito.aplicar_descuento(10) == 90000


def test_descuento_invalido():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Mesa", 50000, 1))

    with pytest.raises(ValueError):
        carrito.aplicar_descuento(120)


def test_resumen_contiene_total():
    carrito = Carrito()
    carrito.agregar_producto(Producto("Audífonos", 20000, 2))

    resumen = carrito.resumen()

    assert "RESUMEN DE COMPRA" in resumen
    assert "TOTAL: 40000" in resumen
