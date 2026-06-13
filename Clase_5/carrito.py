class Producto:
    def __init__(self, nombre, precio, cantidad):
        if nombre.strip() == "":
            raise ValueError("El nombre del producto no puede estar vacío")

        if precio < 0:
            raise ValueError("El precio no puede ser negativo")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")

        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad

    def subtotal(self):
        return self.precio * self.cantidad


class Carrito:
    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto):
        self.productos.append(producto)

    def eliminar_producto(self, nombre_producto):
        nombre_limpio = nombre_producto.strip().lower()

        for producto in self.productos:
            if producto.nombre.strip().lower() == nombre_limpio:
                self.productos.remove(producto)
                return

        raise ValueError("El producto no se encuentra en el carrito")

    def total(self):
        total = 0
        for producto in self.productos:
            total += producto.subtotal()
        return total

    def aplicar_descuento(self, porcentaje):
        if porcentaje < 0 or porcentaje > 100:
            raise ValueError("El descuento debe estar entre 0 y 100")

        descuento = self.total() * porcentaje / 100
        return self.total() - descuento

    def resumen(self):
        lineas = []
        lineas.append("RESUMEN DE COMPRA")
        lineas.append("-----------------")

        for producto in self.productos:
            linea = f"{producto.nombre} - Cantidad: {producto.cantidad} - Subtotal: {producto.subtotal()}"
            lineas.append(linea)

        lineas.append("-----------------")
        lineas.append(f"TOTAL: {self.total()}")

        return "\n".join(lineas)
