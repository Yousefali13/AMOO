import os
import django
import sys

# أضف مجلد المشروع للمسار
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AMOON_ERP.settings')
django.setup()

# الآن يمكنك الاستيراد من الموديل
from AMOON_app.models import CustomUser, Company, Department


from AMOON_app.models import CustomUser, Message  # استبدل بالنماذج الخاصة بك


from AMOON_app.models import CustomUser, Company
from AMOON_app.models import CustomUser
# البحث عن مستخدمين بدون id
print("الشركة:", company)
print("عدد الموظفين:", employees.count())
for emp in employees:
    print(emp.first_name, emp.last_name)
