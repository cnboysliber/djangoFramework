from django.db import models
from fastuser.models import UserInfo
# Create your models here.


class BaseTable(models.Model):
    """
    公共字段列
    """

    status = models.SmallIntegerField(verbose_name='逻辑状态', default=1, null=False)

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        app_label = 'rbac'


class Role(BaseTable):
    """
    角色
    """
    name = models.CharField(max_length=32, unique=True, verbose_name="角色")
    permissions = models.ManyToManyField("ParentMenu", blank=True, verbose_name="权限")
    # menus = models.ManyToManyField("Menu", blank=True, verbose_name="菜单")
    desc = models.CharField(max_length=50, blank=True, null=True, verbose_name="描述")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ParentMenu(BaseTable):
    """
    父菜单
    """
    name = models.CharField(max_length=30, unique=True, verbose_name="菜单名")
    url = models.CharField(max_length=200, null=True, blank=True, verbose_name="组件")
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")
    path = models.CharField(max_length=50, null=True, blank=True, verbose_name="链接地址")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '父菜单'
        verbose_name_plural = verbose_name
        ordering = ['id']


class ChildMenu(BaseTable):
    """
    子菜单
    """
    name = models.CharField(max_length=30, verbose_name="菜单名")
    url = models.CharField(max_length=50, null=True, blank=True, verbose_name="组件")
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")
    path = models.CharField(max_length=50, null=True, blank=True, verbose_name="链接地址")
    pid = models.ForeignKey(ParentMenu, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父菜单")
    order_id = models.IntegerField(verbose_name='排序', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '子菜单'
        verbose_name_plural = verbose_name
        ordering = ['id']
        unique_together = ('name', 'pid')


# class Role(BaseTable):
#     """
#     角色
#     """
#     name = models.CharField(max_length=32, unique=True, verbose_name="角色")
#     permissions = models.ManyToManyField("ParentMenu", blank=True, verbose_name="权限")
#     # menus = models.ManyToManyField("Menu", blank=True, verbose_name="菜单")
#     desc = models.CharField(max_length=50, blank=True, null=True, verbose_name="描述")
#
#     class Meta:
#         verbose_name = "角色"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.name


