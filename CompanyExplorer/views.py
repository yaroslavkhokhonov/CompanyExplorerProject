from django.db.models import Count
from django.db.models.functions import Substr, Upper
from django.views.generic import DetailView, ListView, TemplateView

from .models import Department, Employee


class Home(TemplateView):
    template_name = 'CompanyExplorer/base.html'


class EmployeeDetail(DetailView):
    model = Employee
    template_name = 'CompanyExplorer/employee_detail.html'
    context_object_name = 'employee'


class EmployeeList(ListView):
    model = Employee
    template_name = 'CompanyExplorer/employees.html'
    paginate_by = 10
    context_object_name = 'employees'
    ordering = 'surname'

    def get_queryset(self):
        department = int(self.request.GET.get('department_filter', '0'))
        is_work = int(self.request.GET.get('is_work_filter', '0'))

        query = super(EmployeeList, self).get_queryset()

        if department:
            query = query.filter(department_id=department)
        if is_work:
            # is_work принимает следущие значения:
            # 0 - фильтр не выбран
            # 1 - фильтр по работающим в компании
            # 2 - фильтр по уволенным
            query = query.filter(end_date__isnull=is_work != 2)

        return query

    def get_context_data(self, **kwargs):
        context = super(EmployeeList, self).get_context_data(**kwargs)

        for param in ['department_filter', 'is_work_filter']:
            context[param] = int(self.request.GET.get(param, '0'))

        context['departments'] = Department.objects.all()
        return context


class AlphabetEmployeeList(ListView):
    model = Employee
    ordering = 'surname'
    context_object_name = 'employees'
    template_name = 'CompanyExplorer/alphabet_employees.html'

    GROUPS_COUNT = 7

    def get_groups(self):
        query = super(AlphabetEmployeeList, self).get_queryset()

        # Счетчики оставшихся элементов и групп для постоянного перерасчета эталона
        left_items, left_groups = query.count(), self.GROUPS_COUNT

        query = query \
            .annotate(letter=Upper(Substr('surname', 1, 1))) \
            .values('letter') \
            .annotate(count=Count('id')) \
            .order_by('letter')

        # Определею "эталон" - оптимальное кол-во элементов в одной группе
        group_size = round(left_items / left_groups) or 1

        first_char, last_char = 'А', 'Я'

        # Создаю текущую группу из первого символа
        group = {
            'letter': first_char,
            'count': 0
        }

        # Результат - список групп в виде [А-В, Д-Я]
        result = []

        for item in query:
            # Если кол-во элементов после добавления станет ближе к эталонному числу, то увеличиваем группу
            if abs(group_size - group['count'] - item['count']) <= abs(group_size - group['count']):
                group['count'] += item['count']
                continue

            # Последнюю группу завершаем последней буквой алфавита вне цикла
            if left_groups == 1:
                break

            # Добавляем группу в результат
            result.append('-'.join([group['letter'], chr(ord(item['letter']) - 1)]))
            left_items -= group['count']
            left_groups -= 1
            group_size = round(left_items / left_groups)
            group = item

        if left_groups == 1 and group['count']:
            result.append('-'.join([group['letter'], last_char]))

        return result

    def get_queryset(self):
        items = super(AlphabetEmployeeList, self).get_queryset()
        start, end = self.request.GET.get('letter', '-').upper().split('-')

        if start and end:
            items = items \
                .annotate(letter=Upper(Substr('surname', 1, 1))) \
                .filter(letter__range=(start, end))\
                .all()

        return items

    def get_context_data(self, **kwargs):
        context = super(AlphabetEmployeeList, self).get_context_data(**kwargs)
        context['letters'] = self.get_groups()
        return context
