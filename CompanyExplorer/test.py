from django.test import TestCase

from .models import Employee, Department


class EmployeeListTestCase(TestCase):
    def test_empty_employee_list(self):
        result = self.client.get('/employees')
        self.assertEqual(result.status_code, 200)
        self.assertQuerysetEqual(result.context.get('employees'), [])

    def test_employee_list(self):
        department = Department(name='1')
        department.save()

        employee = Employee(surname='A', name='a', department_id=department.id)
        employee.save()
        result = self.client.get('/employees')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

    def test_employee_department_filter(self):
        department = Department(name='1')
        department.save()

        employee = Employee(surname='A', name='a', department_id=department.id)
        employee.save()

        result = self.client.get('/employees?department_filter=0')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        result = self.client.get('/employees?department_filter=1')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        result = self.client.get('/employees?department_filter=2')
        self.assertQuerysetEqual(result.context.get('employees'), [])

    def test_employee_is_work_filter(self):
        employee = Employee(surname='A', name='a', end_date='1999-01-01')
        employee.save()
        result = self.client.get('/employees?is_work_filter=0')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        result = self.client.get('/employees?is_work_filter=1')
        self.assertQuerysetEqual(result.context.get('employees'), [])

        result = self.client.get('/employees?is_work_filter=2')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        employee.end_date = None
        employee.save()

        result = self.client.get('/employees?is_work_filter=0')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        result = self.client.get('/employees?is_work_filter=1')
        self.assertQuerysetEqual(result.context.get('employees'), ['<Employee: #1 a>'])

        result = self.client.get('/employees?is_work_filter=2')
        self.assertQuerysetEqual(result.context.get('employees'), [])


class EmployeeDetailTest(TestCase):
    def test_new_employee(self):
        department = Department(name='1')
        department.save()

        employee = Employee(surname='t', name='t', patronymic='t', department_id=department.id, position='t', phone='t',
                            email='t', start_date='2016-01-01', end_date='2017-01-01', birthday='1990-01-01')
        employee.save()

        result = self.client.get('/employee/1')
        self.assertEqual(result.context.get('employee'), employee)


class AlphabetEmployeeListTestCase(TestCase):
    def test_alphabet_groupby(self):
        names = 'А', 'В', 'К', 'М', 'О'
        for name in names:
            Employee.objects.create(surname=name)

        result = self.client.get('/alphabet_employees')
        self.assertEqual(result.context.get('letters'), ['А-Б', 'В-Й', 'К-Л', 'М-Н', 'О-Я'])

    def test_alphabet_filter(self):
        names = 'А', 'В', 'К', 'М', 'О'
        for name in names:
            Employee.objects.create(surname=name, name=name)

        result = self.client.get('/alphabet_employees?letter=А-Б')
        self.assertQuerysetEqual((result.context.get('employees')), ['<Employee: #1 А>'])
