from pydantic import BaseModel, Field

class Test(BaseModel):
    a: int = Field(default=1, description='a')

class Test2(BaseModel):
    a: int


# t1 = Test(a=1)
# t2 = Test2(a=1)

assert Test.__annotations__ == Test2.__annotations__

print(Test.__annotations__)
print(Test2.__annotations__)

print(Test.model_json_schema())
print(Test2.model_json_schema())