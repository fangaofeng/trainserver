from controlcenter import Dashboard, widgets
from users.models import User


class ModelItemList(widgets.ItemList):
    model = User
    list_display = ('pk', 'name')


class MySingleBarChart(widgets.SingleBarChart):
    # label and series
    values_list = ('name', 'employee_position')
    # Data source
    queryset = User.objects.order_by()
    limit_to = 6


class MyDashboard(Dashboard):

    widgets = (
        ModelItemList,
        widgets.Group([MySingleBarChart], width=widgets.LARGER, height=300),
    )
