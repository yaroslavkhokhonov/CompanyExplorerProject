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
        def glue(a, b):
            return '-'.join([a, b])

        items = super(AlphabetEmployeeList, self).get_queryset()

        # Определею "эталон" - оптимальное кол-во элементов в одной группе
        group_size = round(len(items) / self.GROUPS_COUNT) or 1

        # Счетчики оставшихся элементов для постоянного перерасчета эталона
        uncounted_items, uncounted_groups = len(items), self.GROUPS_COUNT

        first_char, last_char = 'А', 'Я'

        # Кол-во элементов в текущей группе
        count = 0

        # group - количество элементов в текущей группе без символа key_char
        group, key_char = 0, first_char

        # Список символов, каждый их которых является началом новой группы
        # Например, список [A, Д] означает группировку [А-В, Д-Я]
        key_chars = [first_char]

        for item in items:
            cur_char = item.surname[0].upper()

            # Проходим по списку и наращиваем текущую группу, пока символы повторяются
            if key_char == cur_char:
                count += 1
                continue

            # Когда символ не совпадает с предыдущим, проверяем размер группы
            if count >= group_size:
                # Итак, группа больше эталона.
                # Сейчас есть два пути - добавить в группу элементы последнего символа или нет
                # Для этого сравниваю отклонения от эталона в обоих случаях
                if count - group_size <= group_size - group:
                    # Добавляем группу целиком и обнуляем счетчик
                    key_chars.append(cur_char)
                    uncounted_items -= count
                    count = 0
                else:
                    # Добавляем группу без элементов, начинающихся на key_char
                    # Недобавленные элементы остаются в новой группе
                    key_chars.append(key_char)
                    uncounted_items -= group
                    count -= group

                uncounted_groups -= 1
                group_size = round(uncounted_items / uncounted_groups)

            # Если группа меньше эталона - фиксируем новые ключевые значения и продолжаем цикл
            key_char = cur_char
            group = count
            count += 1

        if group and len(key_chars) < 6:
            # Если в группе остались элементы, то добавляю последнюю группу в результат
            key_chars.append(key_char)

        result = []

        # Преобразую список в нужный формат
        for i, char in enumerate(key_chars[:-1]):
            result.append(glue(char, chr(ord(key_chars[i + 1]) - 1)))

        # Расширяю последнюю группу до конца алфавита
        result.append(glue(key_chars[-1], last_char))

        return result

    def get_queryset(self):
        items = super(AlphabetEmployeeList, self).get_queryset()
        start, end = self.request.GET.get('letter', '-').split('-')

        if start and end:
            items = list(filter(lambda x: start <= x.surname[0] <= end, items))

        return items

    def get_context_data(self, **kwargs):
        context = super(AlphabetEmployeeList, self).get_context_data(**kwargs)
        context['letters'] = self.get_groups()
        return context
