from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, FileField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegisterForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('نوع الحساب', choices=[('funder', 'داعم/مستثمر'), ('project_owner', 'صاحب مشروع')])
    submit = SubmitField('تسجيل حساب')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('هذا البريد الإلكتروني مستخدم بالفعل، الرجاء استخدام بريد آخر')

class ContactForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired(message='يرجى إدخال الاسم')])
    email = EmailField('البريد الإلكتروني', validators=[DataRequired(message='يرجى إدخال البريد الإلكتروني'), Email(message='يرجى إدخال بريد إلكتروني صحيح')])
    subject = StringField('الموضوع', validators=[DataRequired(message='يرجى إدخال موضوع الرسالة')])
    message = TextAreaField('الرسالة', validators=[DataRequired(message='يرجى إدخال محتوى الرسالة')])
    submit = SubmitField('إرسال الرسالة')

# Add other required form classes
class FundingForm(FlaskForm):
    amount = StringField('مبلغ التمويل (ريال)', validators=[
        DataRequired(message='يرجى إدخال مبلغ التمويل'),
        # Add a custom validator to ensure it's a valid number
    ])
    agree_terms = BooleanField('أوافق على الشروط والأحكام', validators=[
        DataRequired(message='يجب الموافقة على الشروط والأحكام')
    ])
    submit = SubmitField('تأكيد التمويل')
    
    def validate_amount(self, field):
        try:
            amount = int(field.data)
            if amount < 100:
                raise ValidationError('مبلغ التمويل يجب أن لا يقل عن 100 ريال')
        except ValueError:
            raise ValidationError('يرجى إدخال مبلغ صحيح')

class ProjectForm(FlaskForm):
    title = StringField('عنوان المشروع', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('وصف المشروع', validators=[DataRequired(), Length(min=100)])
    category = SelectField('فئة المشروع', choices=[
        ('tech', 'تقني'), 
        ('medical', 'طبي'), 
        ('industrial', 'صناعي'),
        ('agricultural', 'زراعي'),
        ('educational', 'تعليمي'),
        ('other', 'أخرى')
    ])
    funding_goal = StringField('هدف التمويل (ريال)', validators=[DataRequired()])
    expected_return = StringField('العائد المتوقع (%)', validators=[DataRequired()])
    image = FileField('صورة المشروع')
    submit = SubmitField('حفظ المشروع')

class ProjectUpdateForm(FlaskForm):
    title = StringField('عنوان التحديث', validators=[DataRequired(), Length(min=5, max=200)])
    content = TextAreaField('محتوى التحديث', validators=[DataRequired(), Length(min=50)])
    update_type = SelectField('نوع التحديث', choices=[
        ('milestone', 'إنجاز مرحلة'),
        ('progress', 'تقرير تقدم'),
        ('financial', 'تحديث مالي'),
        ('other', 'آخر')
    ])
    submit = SubmitField('نشر التحديث')

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    profile_image = FileField('الصورة الشخصية')
    submit = SubmitField('تحديث البيانات')

class ProjectReviewForm(FlaskForm):
    status = SelectField('قرار المراجعة', choices=[
        ('funding', 'موافقة - نشر للتمويل'),
        ('rejected', 'رفض')
    ])
    admin_notes = TextAreaField('ملاحظات للمستخدم')
    submit = SubmitField('حفظ المراجعة')
