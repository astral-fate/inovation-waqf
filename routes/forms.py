from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email
from datetime import datetime, timedelta

# Project categories
PROJECT_CATEGORIES = [
    ('tech', 'تقني'),
    ('medical', 'طبي'),
    ('industrial', 'صناعي'),
    ('agricultural', 'زراعي'),
    ('educational', 'تعليمي'),
    ('environmental', 'بيئي'),
    ('energy', 'طاقة'),
    ('other', 'أخرى')
]

class ProjectForm(FlaskForm):
    title = StringField('عنوان المشروع', validators=[DataRequired(), Length(min=5, max=200)])
    category = SelectField('فئة المشروع', choices=PROJECT_CATEGORIES, validators=[DataRequired()])
    description = TextAreaField('وصف المشروع', validators=[DataRequired(), Length(min=50)])
    funding_goal = FloatField('المبلغ المطلوب (ريال)', validators=[DataRequired(), NumberRange(min=1000)])
    expected_return = StringField('العائد المتوقع (مثل: ١٥-٢٠٪)', validators=[DataRequired()])
    funding_duration = SelectField('مدة التمويل', choices=[
        ('30', '٣٠ يوم'),
        ('60', '٦٠ يوم'),
        ('90', '٩٠ يوم')
    ], validators=[DataRequired()])
    image = FileField('صورة المشروع', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'يرجى تحميل صورة فقط!')
    ])
    submit = SubmitField('إرسال المشروع للمراجعة')

class ProjectReviewForm(FlaskForm):
    status = SelectField('حالة المشروع', choices=[
        ('approved', 'موافقة - عرض للتمويل'),
        ('rejected', 'رفض')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ القرار')

class FundingForm(FlaskForm):
    amount = FloatField('مبلغ التمويل (ريال)', validators=[DataRequired(), NumberRange(min=100)])
    submit = SubmitField('تأكيد الدعم')

class ProjectUpdateForm(FlaskForm):
    title = StringField('عنوان التحديث', validators=[DataRequired(), Length(min=5, max=200)])
    content = TextAreaField('محتوى التحديث', validators=[DataRequired(), Length(min=20)])
    update_type = SelectField('نوع التحديث', choices=[
        ('general', 'تحديث عام'),
        ('milestone', 'إنجاز مرحلة'),
        ('return', 'توزيع عوائد')
    ], validators=[DataRequired()])
    submit = SubmitField('نشر التحديث')

class ContactForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    subject = StringField('الموضوع', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('الرسالة', validators=[DataRequired(), Length(min=20)])
    submit = SubmitField('إرسال')

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    profile_image = FileField('الصورة الشخصية', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'يرجى تحميل صورة فقط!')
    ])
    submit = SubmitField('تحديث الملف الشخصي')