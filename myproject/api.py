from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema, UploadedFile, File
from django.core.files.storage import FileSystemStorage

from django.db import models
from datetime import date

api = NinjaAPI()
STORAGE = FileSystemStorage()


class HelloSchema(Schema):
    name: str = "World"


class UserSchema(Schema):
    username: str
    email: str
    first_name: str
    last_name: str


class Error(Schema):
    message: str




##########################################################################
class Department(models.Model):
    title = models.CharField(max_length=100)


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)



class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: int | None = None
    birthdate: date | None = None

    class Config:
        extra = "forbid"

class EmployeeOut(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int | None = None
    birthdate: date | None= None


##########################################################################


# @api.post("/employees")
# def create_employee(request, payload: EmployeeIn):
#     employee = Employee.objects.create(**payload.dict())
#     return {"id": employee.id}

@api.post("/employees")
def create_employee(request, payload: EmployeeIn, cv: File[UploadedFile] = None):
    payload_dict = payload.dict()
    employee = Employee(**payload_dict)
    employee.cv.save(cv.name, cv)
    return {"id": employee.id}


# handle file upload
@api.post("/upload")
def create_file(request, file: File[UploadedFile]):
    filename = STORAGE.save(file.name, file)
    return {"filename": filename}

# get single employee
@api.get("/employees/{employee_id}", response=EmployeeOut)
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return employee

# get all employees
@api.get("/employees", response=list[EmployeeOut])
def get_employees(request):
    employees = Employee.objects.all()
    return employees

# update employee
@api.put("/employees/{employee_id}")
def update_employee(request, employee_id: int, payload: EmployeeIn):
    """
    To allow the user to make partial updates, 
    use `payload.dict(exclude_unset=True).items()`. 
    This ensures that only the specified fields get updated.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    for attr, value in payload.dict().items():
        setattr(employee, attr, value)
    employee.save()
    return {"success": True}

# delete employee
@api.delete("/employees/{employee_id}")
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {"success": True}



##########################################################################
##########################################################################
##########################################################################


@api.get("/me", response={200: UserSchema, 403: Error})
def me(request):
    if not request.user.is_authenticated:
        return 403, Error(message="Not authenticated")
    return request.user


# @api.get("/me", response=UserSchema)
# def me(request):
#     return request.user


@api.post("/hello")
def hello(request, data: HelloSchema):
    # get name from query params
    return f"Hello {data.name}"


# @api.get("/hello")
# def hello(request, name: str = "World"):
#     # get name from query params
#     return f"Hello {name}"


# @api.get("/math")
# def math(request, a: int = 1, b: int = 1):
#     return {
#         "add": a + b,
#         "subtract": a - b,
#         "multiply": a * b,
#         "divide": a / b,
#     }


@api.get("/math/{a}and{b}")
def math2(request, a: int, b: int):
    # get a and b from path params
    return {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b,
    }
