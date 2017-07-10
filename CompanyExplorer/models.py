from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=30)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '#{} {}'.format(self.id, self.name)

    class Meta:
        verbose_name_plural = 'Отделы'
        verbose_name = 'Отдел'


class Employee(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=50, blank=True, null=True)
    surname = models.CharField(verbose_name='Фамилия', max_length=50)
    patronymic = models.CharField(verbose_name='Отчество', max_length=50, blank=True, null=True)
    birthday = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    email = models.CharField(verbose_name='Эл. почта', max_length=50, blank=True, null=True)
    phone = models.CharField(verbose_name='Телефон', max_length=12, blank=True, null=True)

    start_date = models.DateField(verbose_name='Дата начала работы', blank=True, null=True)
    end_date = models.DateField(verbose_name='Дата окончания работы', blank=True, null=True)
    position = models.CharField(verbose_name='Должность', max_length=50, blank=True, null=True)
    department = models.ForeignKey(Department, verbose_name='Отдел', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '#{} {}'.format(self.id, self.name)

    class Meta:
        verbose_name_plural = 'Сотрудники'
        verbose_name = 'Сотрудник'
