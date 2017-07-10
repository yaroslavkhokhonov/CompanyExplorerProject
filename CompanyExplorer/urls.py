from django.conf.urls import url

from CompanyExplorer.random_data_generator import RandomGenerator
from . import views


urlpatterns = [
    url(r'^$', views.Home.as_view()),
    url(r'^employee/(?P<pk>[0-9]+)$', views.EmployeeDetail.as_view()),
    url(r'^alphabet_employees', views.AlphabetEmployeeList.as_view()),
    url(r'^employees$', views.EmployeeList.as_view()),
    url(r'^create_random_employees$', RandomGenerator.as_view())
]
