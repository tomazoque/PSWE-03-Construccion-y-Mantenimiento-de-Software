import requests

URL_BASE = "http://127.0.0.1:5000"


def probar_api():
    try:
        respuesta = requests.get(f"{URL_BASE}/", timeout=5)

        if respuesta.status_code == 200:
            print("API disponible")
            print(respuesta.json())
        else:
            print("La API respondió, pero con error")

    except requests.exceptions.ConnectionError:
        print("Error: no se pudo conectar con la API.")
    except requests.exceptions.Timeout:
        print("Error: la API tardó demasiado en responder.")


def listar_productos():
    try:
        respuesta = requests.get(f"{URL_BASE}/productos", timeout=5)

        if respuesta.status_code == 200:
            productos = respuesta.json()

            print("\nLista de productos")
            print("------------------")

            for producto in productos:
                print(f"ID: {producto['id']}")
                print(f"Nombre: {producto['nombre']}")
                print(f"Precio: {producto['precio']}")
                print(f"Stock: {producto['stock']}")
                print("------------------")
        else:
            print("Error consultando productos.")

    except requests.exceptions.ConnectionError:
        print("Error: no se pudo conectar con la API.")


def buscar_producto():
    try:
        id_producto = int(input("Digite el ID del producto: "))

        respuesta = requests.get(
            f"{URL_BASE}/productos/{id_producto}",
            timeout=5
        )

        if respuesta.status_code == 200:
            producto = respuesta.json()

            print("\nProducto encontrado")
            print("-------------------")
            print(f"ID: {producto['id']}")
            print(f"Nombre: {producto['nombre']}")
            print(f"Precio: {producto['precio']}")
            print(f"Stock: {producto['stock']}")

        elif respuesta.status_code == 404:
            print("Producto no encontrado.")
        else:
            print("Error inesperado.")

    except ValueError:
        print("Debe digitar un número.")
    except requests.exceptions.ConnectionError:
        print("Error: no se pudo conectar con la API.")


def registrar_venta():
    try:
        id_producto = int(input("Digite el ID del producto: "))
        cantidad = int(input("Digite la cantidad: "))

        datos = {
            "id_producto": id_producto,
            "cantidad": cantidad
        }

        respuesta = requests.post(
            f"{URL_BASE}/ventas",
            json=datos,
            timeout=5
        )

        resultado = respuesta.json()

        if respuesta.status_code == 201:
            print("\nVenta registrada")
            print("----------------")
            print(f"Producto: {resultado['producto']}")
            print(f"Cantidad: {resultado['cantidad']}")
            print(f"Precio unitario: {resultado['precio_unitario']}")
            print(f"Total: {resultado['total']}")
            print(f"Stock restante: {resultado['stock_restante']}")
        else:
            print("\nNo se pudo registrar la venta")
            print(f"Error: {resultado.get('error')}")

    except ValueError:
        print("Debe digitar valores numéricos.")
    except requests.exceptions.ConnectionError:
        print("Error: no se pudo conectar con la API.")


def menu():
    while True:
        print("\nCliente de ventas")
        print("1. Probar conexión con API")
        print("2. Listar productos")
        print("3. Buscar producto")
        print("4. Registrar venta")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            probar_api()
        elif opcion == "2":
            listar_productos()
        elif opcion == "3":
            buscar_producto()
        elif opcion == "4":
            registrar_venta()
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()