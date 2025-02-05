import functools

class MinhaClasse:
    def meu_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            print(f"Executando {func.__name__} dentro de {self.__class__.__name__}")
            return func(self, *args, **kwargs)  # Chama o método original
        return wrapper

    @meu_decorator
    def metodo(self, x):
        print(f"Processando {x}")

# Uso
obj = MinhaClasse()
obj.metodo(42)
