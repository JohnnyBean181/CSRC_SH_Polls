from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Question, Choice, Employees, Departments, Titles
from .models import DeptManager, VoterTitles, Voters2024, Scales, Votes
from .admin_form import TitleForm, EmployeeForm, DeptManagerForm


#class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

# Register your models here.
# admin.site.register(Question, QuestionAdmin)

@admin.register(Departments)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['dept_name', 'created_date', 'location']

class TitleAdmin(admin.ModelAdmin):
    form = TitleForm
# don't display in production
# admin.site.register(Titles, TitleAdmin)

class DepartmentInline(admin.StackedInline):
    model = Departments

class TitleInline(admin.StackedInline):
    model = Titles

@admin.register(Employees)
class EmployeeAdmin(admin.ModelAdmin):
    inlines = [TitleInline]
    list_display = ['emp_no', 'get_fullname', 'get_departments', 'get_title']
    form = EmployeeForm
    list_per_page = 15  # 设置每页显示的记录条数

    def get_fullname(self, obj):
        return f"{obj.last_name}{obj.first_name}"

    get_fullname.short_description = "姓名"

    def save_model(self, request, obj, form, change):
        # 先保存 Employee 实例
        super().save_model(request, obj, form, change)

        # 处理多对多的 Department 并创建 Management 记录
        if 'departments' in form.cleaned_data:
            departments = form.cleaned_data['departments']
            # 删除旧的 Management 记录（可选）
            DeptManager.objects.filter(emp_no=obj).delete()
            # 创建新的 Management 记录
            for department in departments:
                DeptManager.objects.create(emp_no=obj, dept_no=department)

    def get_departments(self, obj):
        # 查询通过 DeptManager 表与 Employee 关联的部门
        departments = Departments.objects.filter(deptmanager__emp_no=obj)
        return ", ".join([dept.dept_name for dept in departments])

        # optimized version
        # departments = obj.deptmanager_set.prefetch_related('dept_no')
        # return ", ".join([dm.dept_no.dept_name for dm in departments])

    get_departments.short_description = '部门'

    def get_title(self, obj):
        titles = Titles.objects.filter(emp_no=obj)
        return ", ".join([i.title for i in titles])

    get_title.short_description = "职级"

class DeptManagerAdmin(admin.ModelAdmin):
    form = DeptManagerForm
# don't display in production
# admin.site.register(DeptManager, DeptManagerAdmin)

admin.site.register(VoterTitles)

@admin.register(Voters2024)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {'fields': ('emp_no', 'voter_id', 'dept_no')}),
        ("Status", {'fields': ('voted', 'valid_year')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {'fields': ('emp_no', 'voter_id', 'dept_no')}),
        ("Status", {'fields': ('voted', 'valid_year')}),
    )

admin.site.register(Scales)

@admin.register(Votes)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["voter", "emp_no", "scale"]
    search_fields = ["voter__username"]
