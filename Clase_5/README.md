# Clase 5

## La Historia de Usuario

> **Como** cliente,
> **quiero** poder eliminar un producto de mi carrito de compras por su nombre,
> **para** corregir mi orden eliminando artículos que ya no deseo adquirir.

## Los Criterios de Aceptación

* El sistema debe buscar el producto en el carrito por coincidencia exacta de su nombre (ignorando mayúsculas/minúsculas y espacios en blanco).
* Si el producto existe en el carrito, se debe remover de la lista, actualizando el subtotal, el total y el resumen de compra de forma inmediata.
* Si se intenta eliminar un producto que no se encuentra en el carrito, el sistema debe lanzar una excepción de tipo `ValueError` con el mensaje claro: `"El producto no se encuentra en el carrito"`.

## La Tarea Técnica

* Modificar la clase `Carrito` en el archivo `carrito.py` para añadir el método `eliminar_producto(self, nombre_producto)`.
* Implementar un ciclo que recorra `self.productos`. Si encuentra una coincidencia, utilizar `.remove()` y salir del método. Si finaliza el ciclo sin coincidencias, lanzar un `ValueError`.