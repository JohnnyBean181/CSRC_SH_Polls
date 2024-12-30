from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from Poll2024.models import Voters2024 as Voter, VoterTitles, Departments, Employees
import random
import pandas as pd


class Command(BaseCommand):
    help = 'Generate user credentials'
    """
    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='Number of users to generate')
    """
    def handle(self, *args, **options):
        num_users = {
            0: 76, # 处级
            1: 9, # 办公室
            2: 2, # 党办
            3: 5, # 调研处
            4: 8, # 公司一处
            5: 8, # 公司二处
            6: 4, # 公司三处
            7: 6, # 债券处
            8: 9, # 机构一处
            9: 6, # 机构二处
            10: 8, # 期货处
            11: 8, # 私募处
            12: 3, # 综合业务处
            13: 11, # 稽查一处
            14: 10, # 稽查二处
            15: 7, # 法治处
            16: 7, # 会计处
            17: 5, # 投保处
            18: 3, # 纪检办
        }

        voters_xlsx = [] # used for exporting to the excel file
        voters_sql = [] # used for creating voters

        titles = VoterTitles.objects.all()
        titles_dict = {title.title_id: title for title in titles}

        depts = Departments.objects.all()
        depts_dict = {dept.dept_no: dept for dept in depts}

        """创建处级投票人账户"""
        for _ in range(num_users[0]):
            # for Excel output
            username = ''.join(random.sample("abcdefghjkmnopqrstuvwxyz", 6))
            password_txt = ''.join(random.sample("23456789", 4))
            password = make_password(password_txt)
            voters_xlsx.append({'账号': username,
                                '密码': password_txt,
                                '职级': '处级'})
            # for SQL
            voter = Voter(
                    username=username,
                    password=password,
                    email='user@csrc.gov.com',
                    valid_year=2024,
                    title_id=titles_dict[2],
                )
            voters_sql.append(voter)

        """创建科级投票人账户"""
        for dept_no, users_count in num_users.items():
            if dept_no == 0:
                continue
            for _ in range(users_count):
                # for Excel output
                username = ''.join(random.sample("abcdefghjkmnopqrstuvwxyz", 6))
                password_txt = ''.join(random.sample("23456789", 4))
                password = make_password(password_txt)
                voters_xlsx.append({'账号': username,
                                    '密码': password_txt,
                                    '职级': '科级',
                                    '处室': depts_dict[dept_no].dept_name,})
                # for SQL
                voter = Voter(
                    username=username,
                    password=password,
                    email='user@csrc.gov.com',
                    valid_year=2024,
                    title_id=titles_dict[3],
                    dept_no=depts_dict[dept_no],
                )
                voters_sql.append(voter)

        """创建局级投票人账户"""
        for _ in range(4):
            # for Excel output
            username = ''.join(random.sample("abcdefghjkmnopqrstuvwxyz", 6))
            password_txt = ''.join(random.sample("23456789", 4))
            password = make_password(password_txt)

            voters_xlsx.append({'账号': username,
                                '密码': password_txt,
                                '职级': '局级'}) # 后续要手动添加信息

            # for SQL
            voter = Voter(
                username=username,
                password=password,
                email='user@csrc.gov.com',
                valid_year=2024,
                title_id=titles_dict[1], # 后续要手动添加信息
            )
            voters_sql.append(voter)

        with transaction.atomic():
            # write to SQL
            Voter.objects.bulk_create(voters_sql)

            # export to xlsx
            df = pd.DataFrame(voters_xlsx)
            excel_file_path = 'users.xlsx'
            df.to_excel(excel_file_path, index=False)
            self.stdout.write(self.style.SUCCESS(f"User credentials have been saved to {excel_file_path}"))
