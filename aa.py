from pydantic import BaseModel

class TextOutput(BaseModel):
    @staticmethod
    def action() -> str:
        return 'text'

# Uso
print(TextOutput.action())  # Saída: 'text'
